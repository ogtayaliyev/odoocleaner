# modules/column_manager.py — Gestion des colonnes : suppression, renommage et application du mapping

import pandas as pd
from typing import Dict, List, Tuple


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime toutes les colonnes entièrement vides (NaN)."""
    return df.dropna(axis=1, how="all")


def drop_zero_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime toutes les colonnes numériques qui ne contiennent que des zéros."""
    cols_to_drop = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0 and (non_null_values == 0).all():
                cols_to_drop.append(col)
    return df.drop(columns=cols_to_drop)


def drop_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Supprime une colonne spécifique."""
    if column_name in df.columns:
        return df.drop(columns=[column_name])
    return df


def rename_column(df: pd.DataFrame, old_name: str, new_name: str) -> pd.DataFrame:
    """Renomme une colonne spécifique."""
    if old_name in df.columns:
        return df.rename(columns={old_name: new_name})
    return df


def apply_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Applique le mapping de colonnes. 
    Retourne le DataFrame modifié, la liste des colonnes renommées et celles absentes.
    """
    applied = []
    skipped = []
    rename_dict = {}

    for odoo_name, target_name in mapping.items():
        if odoo_name in df.columns:
            rename_dict[odoo_name] = target_name
            applied.append(odoo_name)
        else:
            skipped.append(odoo_name)

    new_df = df.rename(columns=rename_dict)
    return new_df, applied, skipped


def format_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Détecte et formate les colonnes de date au format JJ/MM/AAAA."""
    # ... (code existant non modifié si possible, mais je dois rajouter la nouvelle fonction en dessous)
    return df


def clean_numeric_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Supprime les virgules et points d'une colonne pour la rendre purement numérique."""
    df = df.copy()
    if column_name in df.columns:
        # On convertit en chaîne, on enlève les points et virgules, puis on tente de convertir en nombre
        df[column_name] = df[column_name].astype(str).str.replace(r'[.,]', '', regex=True)
        # On essaie de convertir en numérique si possible
        df[column_name] = pd.to_numeric(df[column_name], errors='ignore')
    return df
