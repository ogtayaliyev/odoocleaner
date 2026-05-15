# main.py — Application principale Streamlit : interface utilisateur complète pour nettoyer les exports Excel Odoo

import sys
import os
import json
import io
import copy
from typing import Optional

import streamlit as st
import pandas as pd

# ─── Chemin de base ──────────────────────────────────────────────────────────

def get_base_path() -> str:
    """Retourne le chemin racine, compatible PyInstaller et mode développement."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = get_base_path()
MAPPING_PATH = os.path.join(BASE_PATH, "config", "mapping.json")

# ─── Modules internes ────────────────────────────────────────────────────────
sys.path.insert(0, BASE_PATH)
from modules.analyzer import analyze_dataframe
from modules.column_manager import (
    drop_empty_columns,
    drop_zero_columns,
    drop_column,
    rename_column,
    apply_mapping,
    format_date_columns,
)
from modules.row_manager import drop_empty_rows, drop_rows_where_zero
from modules.exporter import export_excel, export_csv

# ─── Configuration Streamlit ─────────────────────────────────────────────────
st.set_page_config(
    page_title="OdooExcelCleaner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personnalisé ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .main-header h1 { color: #e2e8f0; font-size: 2rem; font-weight: 700; margin: 0; }
    .main-header p  { color: #94a3b8; margin: 0.4rem 0 0; font-size: 0.95rem; }

    .stat-card {
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .stat-card .value { font-size: 2rem; font-weight: 700; color: #ffffff; }
    .stat-card .label { font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }

    .action-badge {
        display: inline-block;
        background: rgba(99,179,237,0.12);
        border: 1px solid rgba(99,179,237,0.3);
        border-radius: 20px;
        padding: .2rem .75rem;
        font-size: 0.78rem;
        color: #63b3ed;
        margin: .15rem;
    }
    .warning-box {
        background: rgba(245,158,11,0.1);
        border: 1px solid rgba(245,158,11,0.4);
        border-radius: 10px;
        padding: .8rem 1rem;
        color: #fbbf24;
        font-size: 0.88rem;
    }
    .success-box {
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.4);
        border-radius: 10px;
        padding: .8rem 1rem;
        color: #34d399;
        font-size: 0.88rem;
    }

    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    div[data-testid="stExpander"]  { border-radius: 10px; }

    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all .2s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,.3); }

    .sidebar-section {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: .8rem;
        margin-bottom: .8rem;
        border: 1px solid rgba(255,255,255,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── En-tête ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🧹 OdooExcelCleaner</h1>
        <p>Nettoyage et renommage d'exports Excel Odoo — interface professionnelle</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Chargement du mapping ────────────────────────────────────────────────────

def load_mapping() -> dict:
    """Charge le mapping JSON, crée un fichier d'exemple si absent."""
    os.makedirs(os.path.dirname(MAPPING_PATH), exist_ok=True)
    if not os.path.exists(MAPPING_PATH):
        default = {
            "Lignes de facture/BU": "BU",
            "Delivery mode": "Mode de livraison",
            "Prix unitaire": "Prix HT",
        }
        with open(MAPPING_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        st.toast("⚠️ mapping.json créé avec des exemples — pensez à le personnaliser !", icon="⚠️")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_mapping(mapping: dict) -> None:
    """Sauvegarde le mapping dans le fichier JSON."""
    os.makedirs(os.path.dirname(MAPPING_PATH), exist_ok=True)
    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


# ─── Initialisation session_state ────────────────────────────────────────────

def init_state() -> None:
    defaults = {
        "authenticated": False,   # État de connexion
        "df_original": None,      # DataFrame original — jamais modifié
        "df_current": None,       # DataFrame de travail courant
        "history": [],            # Liste de DataFrames pour Annuler
        "action_log": [],         # Journal des actions textuelles
        "mapping": load_mapping(),
        "file_name": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# ─── Authentification ────────────────────────────────────────────────────────

def login_page():
    """Affiche une page de connexion élégante et centrée."""
    st.markdown(
        """
        <style>
        /* On masque les menus Streamlit sur la page de login pour un look pur app */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 5rem;
        }

        .login-container {
            width: 100%;
            max-width: 450px;
            padding: 3rem;
            background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            text-align: center;
        }
        
        .login-logo {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            display: block;
        }

        .login-title {
            color: #ffffff;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .login-subtitle {
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 2rem;
        }

        /* Style spécifique pour les inputs dans le container */
        div[data-testid="stTextInput"] label {
            color: #cbd5e1 !important;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<span class="login-logo">🧹</span>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">OdooExcelCleaner</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Connectez-vous pour accéder à votre espace de nettoyage</div>', unsafe_allow_html=True)
        
        user = st.text_input("Utilisateur", placeholder="Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Se connecter au tableau de bord", use_container_width=True, type="primary"):
            if user == "Techlab" and pwd == "Techlab":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Identifiants incorrects. Veuillez réessayer.")
        
        st.markdown('<div style="margin-top: 2rem; font-size: 0.8rem; color: #475569;">Techlab Deployment System v1.0</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    login_page()
    st.stop()

# ─── Helpers ─────────────────────────────────────────────────────────────────

def push_history(label: str) -> None:
    """Sauvegarde l'état courant dans l'historique avant une action."""
    st.session_state.history.append(copy.deepcopy(st.session_state.df_current))
    st.session_state.action_log.append(label)


def undo() -> None:
    if st.session_state.history:
        st.session_state.df_current = st.session_state.history.pop()
        if st.session_state.action_log:
            st.session_state.action_log.pop()
        st.toast("↩️ Action annulée", icon="↩️")


def reset_to_original() -> None:
    st.session_state.df_current = copy.deepcopy(st.session_state.df_original)
    st.session_state.history = []
    st.session_state.action_log = []
    st.toast("🔄 Fichier réinitialisé à l'original", icon="🔄")


# ─── Sidebar : Upload + Historique ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Chargement du fichier")
    uploaded = st.file_uploader(
        "Déposez un fichier Excel ou CSV",
        type=["xlsx", "xls", "csv"],
        label_visibility="collapsed",
    )

    if uploaded:
        fname = uploaded.name
        ext = fname.rsplit(".", 1)[-1].lower()
        try:
            if ext == "csv":
                df_raw = pd.read_csv(uploaded, encoding="utf-8-sig")
            else:
                try:
                    # Tentative standard avec openpyxl (xlsx)
                    df_raw = pd.read_excel(uploaded, engine="openpyxl")
                except Exception:
                    # Repli sur le moteur par défaut (peut gérer xls ou formats hybrides)
                    uploaded.seek(0)
                    df_raw = pd.read_excel(uploaded)

            if (
                st.session_state.file_name != fname
                or st.session_state.df_original is None
            ):
                st.session_state.df_original = df_raw.copy()
                st.session_state.df_current = df_raw.copy()
                st.session_state.history = []
                st.session_state.action_log = []
                st.session_state.file_name = fname
                st.success(f"✅ **{fname}** chargé — {len(df_raw)} lignes, {len(df_raw.columns)} colonnes")
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")

    st.markdown("---")

    # Historique des actions
    if st.session_state.action_log:
        st.markdown("### 📜 Historique des actions")
        for i, act in enumerate(reversed(st.session_state.action_log[-8:]), 1):
            st.markdown(f'<span class="action-badge">{act}</span>', unsafe_allow_html=True)

        col_u, col_r = st.columns(2)
        with col_u:
            if st.button("↩️ Annuler", use_container_width=True):
                undo()
                st.rerun()
        with col_r:
            if st.button("🔄 Reset", use_container_width=True, type="secondary"):
                reset_to_original()
                st.rerun()
    else:
        if st.session_state.df_current is not None:
            st.markdown(
                '<div class="success-box">✅ Aucune modification — fichier original</div>',
                unsafe_allow_html=True,
            )

# ─── Corps principal ──────────────────────────────────────────────────────────

if st.session_state.df_current is None:
    st.markdown(
        """
        <div style="text-align:center; padding:4rem 2rem; color:#64748b;">
            <div style="font-size:4rem;">📊</div>
            <h3 style="color:#94a3b8;">Aucun fichier chargé</h3>
            <p>Utilisez le panneau de gauche pour importer votre export Excel ou CSV Odoo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

df: pd.DataFrame = st.session_state.df_current
analysis = analyze_dataframe(df)

# ── Statistiques globales ─────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
stats = [
    (len(df), "Lignes"),
    (len(df.columns), "Colonnes"),
    (analysis["empty_cols_count"], "Colonnes vides"),
    (analysis["zero_cols_count"], "Colonnes à zéro"),
    (f"{analysis['fill_rate']:.0f}%", "Taux de remplissage"),
]
for col, (val, label) in zip([c1, c2, c3, c4, c5], stats):
    with col:
        st.markdown(
            f'<div class="stat-card"><div class="value">{val}</div>'
            f'<div class="label">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Onglets principaux ────────────────────────────────────────────────────────
tab_clean_col, tab_clean_row, tab_mapping, tab_export = st.tabs(
    ["🗂️ Colonnes", "📋 Lignes", "🔤 Mapping", "💾 Export"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — Colonnes
# ═══════════════════════════════════════════════════════════════════════════════
with tab_clean_col:
    st.subheader("Analyse des colonnes")

    # Tableau d'analyse
    fill_df = pd.DataFrame(
        [
            {
                "Colonne": col,
                "Non-vides": analysis["col_stats"][col]["non_null"],
                "Remplissage (%)": f"{analysis['col_stats'][col]['fill_pct']:.1f}%",
                "Vide": "✅" if analysis["col_stats"][col]["is_empty"] else "—",
                "Tout à zéro": "✅" if analysis["col_stats"][col]["is_zero"] else "—",
            }
            for col in df.columns
        ]
    )
    st.dataframe(fill_df, use_container_width=True, height=220)

    st.subheader("Actions sur les colonnes")
    ca, cb, cc = st.columns([1, 1, 2])

    with ca:
        if st.button("🗑️ Supprimer colonnes vides", use_container_width=True, type="primary"):
            if analysis["empty_cols_count"] > 0:
                push_history("Suppression colonnes vides")
                st.session_state.df_current = drop_empty_columns(df)
                st.toast(f"✅ {analysis['empty_cols_count']} colonne(s) vide(s) supprimée(s)")
                st.rerun()
            else:
                st.toast("Aucune colonne vide détectée.")

    with cb:
        if st.button("🗑️ Supprimer colonnes à zéro", use_container_width=True):
            if analysis["zero_cols_count"] > 0:
                push_history("Suppression colonnes à zéro")
                st.session_state.df_current = drop_zero_columns(df)
                st.toast(f"✅ {analysis['zero_cols_count']} colonne(s) à zéro supprimée(s)")
                st.rerun()
            else:
                st.toast("Aucune colonne à zéro détectée.")

    with cc:
        with st.expander("✏️ Renommer une colonne", expanded=False):
            col_to_rename = st.selectbox("Colonne à renommer", df.columns.tolist(), key="rename_sel")
            new_name = st.text_input("Nouveau nom", key="rename_new")
            if st.button("Valider le renommage", key="btn_rename"):
                if new_name.strip():
                    push_history(f"Renommage : {col_to_rename} → {new_name.strip()}")
                    st.session_state.df_current = rename_column(df, col_to_rename, new_name.strip())
                    st.toast(f"✅ Colonne renommée : {col_to_rename} → {new_name.strip()}")
                    st.rerun()
                else:
                    st.warning("Entrez un nouveau nom.")

    with st.expander("➖ Supprimer une colonne spécifique", expanded=False):
        col_to_drop = st.selectbox("Colonne à supprimer", df.columns.tolist(), key="drop_col_sel")
        if st.button("Supprimer cette colonne", key="btn_drop_col", type="primary"):
            push_history(f"Suppression colonne : {col_to_drop}")
            st.session_state.df_current = drop_column(df, col_to_drop)
            st.toast(f"✅ Colonne supprimée : {col_to_drop}")
            st.rerun()

    st.markdown("---")
    st.subheader("📅 Formatage des dates")
    st.info("Sélectionnez les colonnes à formater en **JJ/MM/AAAA**.")
    
    date_cols_to_format = st.multiselect(
        "Choisir les colonnes de date", 
        df.columns.tolist(),
        key="date_format_select"
    )
    
    if st.button("📅 Formater les colonnes sélectionnées", use_container_width=True):
        if date_cols_to_format:
            push_history(f"Formatage dates: {', '.join(date_cols_to_format)}")
            
            # Application manuelle sur les colonnes choisies
            temp_df = df.copy()
            for col in date_cols_to_format:
                try:
                    temp_df[col] = pd.to_datetime(temp_df[col], errors='coerce').dt.strftime('%d/%m/%Y')
                except:
                    st.error(f"Impossible de formater la colonne {col}")
            
            st.session_state.df_current = temp_df
            st.success(f"✅ {len(date_cols_to_format)} colonne(s) formatée(s)")
            st.rerun()
        else:
            st.warning("Veuillez sélectionner au moins une colonne.")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — Lignes
# ═══════════════════════════════════════════════════════════════════════════════
with tab_clean_row:
    st.subheader("Nettoyage des lignes")

    ra, rb = st.columns(2)
    with ra:
        empty_row_count = int(df.isnull().all(axis=1).sum())
        st.metric("Lignes entièrement vides", empty_row_count)
        if st.button("🗑️ Supprimer lignes vides", use_container_width=True, type="primary"):
            if empty_row_count > 0:
                push_history("Suppression lignes vides")
                st.session_state.df_current = drop_empty_rows(df)
                st.toast(f"✅ {empty_row_count} ligne(s) vide(s) supprimée(s)")
                st.rerun()
            else:
                st.toast("Aucune ligne vide détectée.")

    with rb:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            col_zero_filter = st.selectbox(
                "Colonne cible (supprimer si = 0)", numeric_cols, key="row_zero_col"
            )
            row_count_zero = int((df[col_zero_filter] == 0).sum())
            st.metric(f"Lignes où {col_zero_filter} = 0", row_count_zero)
            if st.button("🗑️ Supprimer ces lignes", use_container_width=True):
                if row_count_zero > 0:
                    push_history(f"Suppression lignes où {col_zero_filter}=0")
                    st.session_state.df_current = drop_rows_where_zero(df, col_zero_filter)
                    st.toast(f"✅ {row_count_zero} ligne(s) supprimée(s)")
                    st.rerun()
                else:
                    st.toast("Aucune ligne à supprimer.")
        else:
            st.markdown(
                '<div class="warning-box">⚠️ Aucune colonne numérique détectée dans ce fichier.</div>',
                unsafe_allow_html=True,
            )

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — Mapping
# ═══════════════════════════════════════════════════════════════════════════════
with tab_mapping:
    st.subheader("Gestion du mapping de colonnes")
    mapping: dict = st.session_state.mapping

    st.markdown(
        f"**Fichier :** `{MAPPING_PATH}`  "
        f"— **{len(mapping)}** correspondance(s) définie(s)"
    )

    # Tableau du mapping actuel
    if mapping:
        map_df = pd.DataFrame(
            [{"Nom Odoo (original)": k, "Nom final souhaité": v} for k, v in mapping.items()]
        )
        st.dataframe(map_df, use_container_width=True, height=200)
    else:
        st.info("Le mapping est vide. Ajoutez des correspondances ci-dessous.")

    # Actions mapping
    m1, m2 = st.columns(2)

    with m1:
        with st.expander("➕ Ajouter / Modifier une correspondance", expanded=False):
            odoo_key = st.text_input("Nom Odoo (colonne source)", key="map_key")
            final_val = st.text_input("Nom final souhaité", key="map_val")
            if st.button("Enregistrer", key="btn_map_add"):
                if odoo_key.strip() and final_val.strip():
                    st.session_state.mapping[odoo_key.strip()] = final_val.strip()
                    save_mapping(st.session_state.mapping)
                    st.toast(f"✅ Correspondance enregistrée : {odoo_key.strip()} → {final_val.strip()}")
                    st.rerun()
                else:
                    st.warning("Remplissez les deux champs.")

    with m2:
        with st.expander("🗑️ Supprimer une correspondance", expanded=False):
            if mapping:
                key_to_del = st.selectbox("Correspondance à supprimer", list(mapping.keys()), key="map_del")
                if st.button("Supprimer", key="btn_map_del", type="primary"):
                    del st.session_state.mapping[key_to_del]
                    save_mapping(st.session_state.mapping)
                    st.toast(f"✅ Correspondance supprimée : {key_to_del}")
                    st.rerun()
            else:
                st.info("Aucune correspondance à supprimer.")

    st.markdown("---")
    if st.button("🔤 Appliquer le mapping sur le fichier chargé", type="primary"):
        push_history("Application du mapping")
        st.session_state.df_current, applied, skipped = apply_mapping(df, st.session_state.mapping)
        st.toast(f"✅ {len(applied)} colonne(s) renommée(s), {len(skipped)} absente(s) du fichier (ignorées)")
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 4 — Export
# ═══════════════════════════════════════════════════════════════════════════════
with tab_export:
    st.subheader("Export du fichier nettoyé")

    ex1, ex2, ex3 = st.columns(3)
    base_name = (st.session_state.file_name or "export").rsplit(".", 1)[0]

    with ex1:
        excel_bytes = export_excel(df)
        st.download_button(
            label="📥 Télécharger en Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"{base_name}_nettoyé.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

    with ex2:
        csv_bytes = export_csv(df)
        st.download_button(
            label="📥 Télécharger en CSV (.csv)",
            data=csv_bytes,
            file_name=f"{base_name}_nettoyé.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with ex3:
        st.metric("Lignes à exporter", len(df))
        st.metric("Colonnes à exporter", len(df.columns))

    st.markdown("---")
    st.subheader("📋 Aperçu du fichier (50 premières lignes)")
    st.dataframe(df.head(50), use_container_width=True, height=400)
