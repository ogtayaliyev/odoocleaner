# modules/exporter.py — Exportation des données : génération de fichiers Excel et CSV en mémoire

import pandas as pd
import io


def export_excel(df: pd.DataFrame) -> bytes:
    """Génère un fichier Excel (.xlsx) en mémoire et retourne les octets."""
    df_export = df.copy()
    
    # Force tous les objets qui ressemblent à des prix (contenant une virgule) en texte 
    # pour empêcher Excel de supprimer les virgules et les zéros inutiles
    for col in df_export.columns:
        if df_export[col].dtype == 'object':
            # Si la colonne contient des virgules, on la traite comme du texte pur pour l'export
            if df_export[col].astype(str).str.contains(',').any():
                df_export[col] = df_export[col].astype(str)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Sheet1")
        # Ajustement automatique de la largeur des colonnes
        worksheet = writer.sheets["Sheet1"]
        for i, col in enumerate(df_export.columns):
            # Calcul sécurisé de la largeur
            max_len = df_export[col].astype(str).str.len().max()
            if pd.isna(max_len): max_len = 10
            column_len = max(max_len, len(col)) + 4
            worksheet.set_column(i, i, column_len)
    return output.getvalue()


def export_csv(df: pd.DataFrame) -> bytes:
    """Génère un fichier CSV en mémoire et retourne les octets (UTF-8 avec BOM pour Excel)."""
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    return output.getvalue().encode("utf-8-sig")
