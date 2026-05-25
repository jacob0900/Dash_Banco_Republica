"""
generate_data.py
Módulo de carga y preparación del dataset de Tasas de Interés (Colocación)
Banco de la República de Colombia – Series históricas mensuales 1998-2025
"""

import os
import pandas as pd
import numpy as np

# Ruta relativa al archivo Excel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "File.xlsx")

# Nombres de columnas limpios
COLUMN_NAMES = [
    "Fecha",
    "CreditosConsumo",
    "CreditosTesoreria",
    "CreditosOrdinarios",
    "CreditosPreferenciales",
    "TasaColocacionBR",
    "TasaColocacionSinTesoreria",
    "TasaColocacionTotal",
]

# Etiquetas legibles para UI
COLUMN_LABELS = {
    "CreditosConsumo":         "Créditos de Consumo (%)",
    "CreditosTesoreria":       "Créditos de Tesorería (%)",
    "CreditosOrdinarios":      "Créditos Ordinarios (%)",
    "CreditosPreferenciales":  "Créditos Preferenciales (%)",
    "TasaColocacionBR":        "Tasa Colocación Banco de la República (%)",
    "TasaColocacionSinTesoreria": "Tasa Colocación sin Tesorería (%)",
    "TasaColocacionTotal":     "Tasa Colocación Total (%)",
}

# Colores pastel para cada serie
# Paleta Obsidian Gold Luxury — 7 tonos dorados/ámbar diferenciados
PALETTE = {
    "CreditosConsumo":            "#F5C842",  # oro brillante
    "CreditosTesoreria":          "#E07B30",         # ámbar cobre
    "CreditosOrdinarios":         "#F9E68C",     # champán
    "CreditosPreferenciales":     "#B8860B",     # oro oscuro
    "TasaColocacionBR":           "#F0A030",         # ámbar naranja
    "TasaColocacionSinTesoreria": "#C8963C",         # bronce dorado
    "TasaColocacionTotal":        "#D4A017",     # oro puro
}


def load_data() -> pd.DataFrame:
    """Carga, limpia y tipifica el dataset desde el archivo Excel."""
    raw = pd.read_excel(FILE_PATH, sheet_name="Series de datos", header=None)

    # Las filas de datos empiezan en el índice 5 (fila 6 en Excel)
    df = raw.iloc[5:].copy()
    df.columns = COLUMN_NAMES

    # Conservar solo filas donde Fecha sea una fecha válida
    df = df[pd.to_datetime(df["Fecha"], errors="coerce").notna()].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Convertir numéricas
    numeric_cols = COLUMN_NAMES[1:]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols)
    df = df.sort_values("Fecha").reset_index(drop=True)

    return df


def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna estadísticas descriptivas de las variables numéricas."""
    numeric_cols = COLUMN_NAMES[1:]
    stats = df[numeric_cols].describe().T.round(2)
    stats.index = [COLUMN_LABELS.get(c, c) for c in stats.index]
    stats.columns = ["Conteo", "Media", "Std", "Mín", "Q1", "Mediana", "Q3", "Máx"]
    return stats


def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna la matriz de correlación de Pearson."""
    numeric_cols = COLUMN_NAMES[1:]
    corr = df[numeric_cols].corr().round(3)
    corr.index   = [COLUMN_LABELS.get(c, c) for c in corr.index]
    corr.columns = [COLUMN_LABELS.get(c, c) for c in corr.columns]
    return corr


# Singleton: cargamos una sola vez al importar el módulo
DF = load_data()
