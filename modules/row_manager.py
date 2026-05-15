# modules/row_manager.py — Gestion des lignes : suppression des lignes vides ou basées sur une valeur zéro

import pandas as pd


def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les lignes où toutes les cellules sont vides."""
    return df.dropna(axis=0, how="all")


def drop_rows_where_zero(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Supprime les lignes où la valeur d'une colonne spécifique est égale à zéro."""
    if column_name in df.columns:
        return df[df[column_name] != 0]
    return df
