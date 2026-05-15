# modules/exporter.py — Exportation des données : génération de fichiers Excel et CSV en mémoire

import pandas as pd
import io


def export_excel(df: pd.DataFrame) -> bytes:
    """Génère un fichier Excel (.xlsx) en mémoire et retourne les octets."""
    # Création d'une copie pour ne pas modifier l'affichage Streamlit
    df_export = df.copy()
    
    output = io.BytesIO()
    # On utilise xlsxwriter pour avoir un contrôle total sur les types Excel
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Sheet1")
        
        workbook  = writer.book
        worksheet = writer.sheets["Sheet1"]
        
        # On définit un format TEXTE strict pour Excel
        text_format = workbook.add_format({'num_format': '@'})

        for i, col in enumerate(df_export.columns):
            # 1. On vérifie si la colonne contient des données qui ressemblent à des prix avec virgule
            # On le fait de manière très large pour ne rien rater
            sample = df_export[col].astype(str)
            if sample.str.contains(',').any():
                # On applique le format TEXTE à TOUTE la colonne dans Excel
                # Cela empêche Excel de transformer "15640,05" en nombre et de casser la virgule
                worksheet.set_column(i, i, None, text_format)
            
            # 2. Ajustement de la largeur
            max_val = sample.str.len().max()
            if pd.isna(max_val): max_val = 10
            column_len = max(max_val, len(col)) + 2
            # Si on n'a pas appliqué le text_format au dessus, on ajuste juste la largeur
            if not sample.str.contains(',').any():
                worksheet.set_column(i, i, column_len)
            else:
                # Si format texte, on ajuste la largeur avec le format
                worksheet.set_column(i, i, column_len, text_format)
                
    return output.getvalue()


def export_csv(df: pd.DataFrame) -> bytes:
    """Génère un fichier CSV en mémoire et retourne les octets (UTF-8 avec BOM pour Excel)."""
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    return output.getvalue().encode("utf-8-sig")
