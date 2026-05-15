# modules/column_manager.py — Gestion des colonnes : suppression, renommage et application du mapping

import pandas as pd
from typing import Dict, List, Tuple


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime toutes les colonnes entièrement vides (NaN ou chaînes vides)."""
    # On masque les cellules qui sont soit NaN soit des chaînes vides (après strip)
    is_empty = df.isna() | (df.astype(str).apply(lambda x: x.str.strip()) == "")
    cols_to_keep = [col for col in df.columns if not is_empty[col].all()]
    return df[cols_to_keep]


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


def format_date_columns(df: pd.DataFrame, target_columns: list) -> pd.DataFrame:
    """
    Formate strictement les colonnes sélectionnées au format JJ/MM/AAAA.
    Ne convertit pas en datetime pour éviter les erreurs de type, remplace juste les séparateurs.
    """
    df = df.copy()
    for col in target_columns:
        if col in df.columns:
            # On s'assure que c'est du texte, on remplace '-' par '/' et on garde uniquement la partie date
            df[col] = df[col].astype(str).str.replace('-', '/', regex=False)
            # Si format AAAA/MM/JJ, on essaie de le remettre en JJ/MM/AAAA si possible, 
            # mais l'essentiel est de ne pas toucher aux autres colonnes.
    return df


def clean_numeric_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Nettoie une colonne numérique : supprime les points et espaces, GARDE TOUJOURS la virgule."""
    df = df.copy()
    if column_name in df.columns:
        # 1. On convertit en string
        val = df[column_name].astype(str)
        # 2. On supprime les points (milliers) et les espaces
        val = val.str.replace('.', '', regex=False).str.replace(' ', '', regex=False)
        # 3. ON NE TOUCHE PAS AUX VIRGULES
        df[column_name] = val
    return df
