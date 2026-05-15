# modules/exporter.py — Exportation des données : génération de fichiers Excel et CSV en mémoire

import pandas as pd
import io


def export_excel(df: pd.DataFrame) -> bytes:
    """Génère un fichier Excel (.xlsx) en mémoire avec protection STRICHTE des virgules."""
    df_export = df.copy()
    
    output = io.BytesIO()
    # Utilisation de l'engine xlsxwriter pour un contrôle cellule par cellule
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # On n'écrit PAS tout de suite avec df.to_excel pour éviter la conversion automatique de pandas
        workbook  = writer.book
        worksheet = workbook.add_worksheet("Sheet1")
        
        # Format Texte strict pour Excel
        text_format = workbook.add_format({'num_format': '@'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})

        # 1. Écrire les en-têtes
        for col_num, value in enumerate(df_export.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # 2. Écrire les données ligne par ligne, cellule par cellule
        for row_num, row_data in enumerate(df_export.values):
            for col_num, cell_value in enumerate(row_data):
                val_str = str(cell_value) if cell_value is not None else ""
                
                # CONDITION CRITIQUE : Si la valeur contient une virgule ou un point,
                # on FORCE l'écriture en tant que TEXTE pour qu'Excel ne touche à rien
                if "," in val_str or "." in val_str:
                    worksheet.write_string(row_num + 1, col_num, val_str, text_format)
                else:
                    # Pour les autres valeurs, écriture normale
                    worksheet.write(row_num + 1, col_num, cell_value)

        # 3. Ajustement de la largeur des colonnes
        for i, col in enumerate(df_export.columns):
            max_len = df_export[col].astype(str).str.len().max()
            if pd.isna(max_len): max_len = 10
            worksheet.set_column(i, i, max_len + 3)
            
    return output.getvalue()


def export_csv(df: pd.DataFrame) -> bytes:
    """Génère un fichier CSV en mémoire et retourne les octets (UTF-8 avec BOM pour Excel)."""
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    return output.getvalue().encode("utf-8-sig")
