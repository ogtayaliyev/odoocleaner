# modules/analyzer.py — Analyse d'un DataFrame : colonnes vides, à zéro, taux de remplissage

from __future__ import annotations

import pandas as pd
from typing import Any


def analyze_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Retourne un dictionnaire d'analyse complet pour un DataFrame :
    - nombre de colonnes vides
    - nombre de colonnes entièrement à zéro (pour colonnes numériques)
    - taux de remplissage global
    - statistiques par colonne
    """
    col_stats: dict[str, dict[str, Any]] = {}
    total_cells = len(df) * len(df.columns) if len(df.columns) > 0 else 1
    total_non_null = 0

    empty_cols_count = 0
    zero_cols_count = 0

    for col in df.columns:
        series = df[col]
        # On considère comme non-vide ce qui n'est pas NaN ET qui n'est pas une chaîne vide
        non_null_mask = series.notna() & (series.astype(str).str.strip() != "")
        non_null = int(non_null_mask.sum())
        is_empty = non_null == 0
        fill_pct = (non_null / len(df) * 100) if len(df) > 0 else 0.0

        # Colonne entièrement à zéro (numérique uniquement)
        is_zero = False
        if not is_empty and pd.api.types.is_numeric_dtype(series):
            non_null_values = series.dropna()
            if len(non_null_values) > 0 and (non_null_values == 0).all():
                is_zero = True

        col_stats[col] = {
            "non_null": non_null,
            "fill_pct": fill_pct,
            "is_empty": is_empty,
            "is_zero": is_zero,
        }

        total_non_null += non_null
        if is_empty:
            empty_cols_count += 1
        if is_zero:
            zero_cols_count += 1

    global_fill_rate = (total_non_null / total_cells * 100) if total_cells > 0 else 0.0

    return {
        "col_stats": col_stats,
        "empty_cols_count": empty_cols_count,
        "zero_cols_count": zero_cols_count,
        "fill_rate": global_fill_rate,
    }
