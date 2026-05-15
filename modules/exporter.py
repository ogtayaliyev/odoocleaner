# modules/exporter.py — Exportation des données : génération de fichiers Excel et CSV en mémoire

import pandas as pd
import io


def export_excel(df: pd.DataFrame) -> bytes:
    """Génère un fichier Excel (.xlsx) en mémoire et retourne les octets."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        # Ajustement automatique de la largeur des colonnes
        worksheet = writer.sheets["Sheet1"]
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
    return output.getvalue()


def export_csv(df: pd.DataFrame) -> bytes:
    """Génère un fichier CSV en mémoire et retourne les octets (UTF-8 avec BOM pour Excel)."""
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    return output.getvalue().encode("utf-8-sig")
