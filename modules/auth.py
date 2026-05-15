import streamlit as st
import os
import json

# Chemin vers le fichier de session persistante
SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "session.json")

def require_auth():
    """Vérifie l'authentification et affiche la page de connexion si nécessaire."""
    
    # 1. Vérifier si on a un fichier de session persistante (pour éviter le login à chaque refresh)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                    if data.get("logged_in") is True:
                        st.session_state.authenticated = True
            except Exception:
                pass

    if not st.session_state.authenticated:
        _display_login_page()
        # Arrête l'exécution du reste du code tant que non authentifié
        st.stop()

def logout():
    """Déconnecte l'utilisateur et efface la session persistante."""
    st.session_state.authenticated = False
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass
    st.rerun()

def _display_login_page():
    """Affiche l'interface de la page de connexion simple et moderne."""
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        /* Cible la colonne du milieu pour lui donner l'aspect d'une carte */
        div[data-testid="column"]:nth-of-type(2) {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 32px;
            padding: 3rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            margin-top: 10vh;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 3 colonnes pour centrer le formulaire
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem; animation: float 3s ease-in-out infinite;">⚡</div>
                <h1 class="gradient-text" style="font-size: 2.5rem; margin-bottom: 0;">OdooExplorer</h1>
                <p style="color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;">Système de Traitement Premium</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        user = st.text_input("NOM D'UTILISATEUR")
        pwd = st.text_input("MOT DE PASSE", type="password", placeholder="••••••••")
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        if st.button("ACCÉDER AU SYSTÈME", use_container_width=True):
            if user == "Techlab" and pwd == "Techlab":
                st.session_state.authenticated = True
                # Sauvegarder l'état pour les refresh
                os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
                with open(SESSION_FILE, "w") as f:
                    json.dump({"logged_in": True}, f)
                st.rerun()
            else:
                st.error("🚫 Accès refusé : Identifiants incorrects")
        
        st.markdown(
            '<div style="margin-top: 2.5rem; text-align: center; font-size: 0.75rem; color: #64748b; letter-spacing: 0.1em; font-weight: 600;">TECHLAB © 2026 • PREMIUM EDITION</div>', 
            unsafe_allow_html=True
        )
