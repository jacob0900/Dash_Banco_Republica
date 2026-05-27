"""
tabs/metodologia.py
Pestaña 6 – Metodología: datos, ETL y enfoque de modelado.
"""

from tabs.svg_icons import svg_icon
from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd


PIPELINE = [
    ("1", "Extracción", "Lectura del archivo Excel del Banco de la República",
     "pd.read_excel() con parsing de fechas y limpieza de encabezados", "#dce8ff"),
    ("2", "Transformación",
     "Renombrado de columnas, conversión de tipos, eliminación de filas no válidas",
     "Filtros de fechas, pd.to_numeric(), dropna()", "#2E2E38"),
    ("3", "Carga",
     "Dataset limpio disponible para análisis y modelado",
     "Módulo generate_data.py con singleton DF", "#fff4dc"),
    ("4", "EDA",
     "Análisis exploratorio: estadísticas, distribuciones, series temporales, correlaciones",
     "Plotly, cálculo de estadísticos descriptivos", "#fde8e8"),
    ("5", "Estacionariedad",
     "Pruebas ADF y KPSS sobre la serie objetivo y su primera diferencia",
     "statsmodels.tsa.stattools: adfuller, kpss", "#f5f0ff"),
    ("6", "Modelado",
     "Construcción del modelo ARIMA con identificación de parámetros (p, d, q)",
     "statsmodels ARIMA, auto_arima (en desarrollo)", "#fef9e7"),
]


def layout():
    df_pipe = pd.DataFrame(PIPELINE, columns=["Fase", "Etapa", "Descripción", "Herramientas", "Color"])

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H3("Metodología",
                            className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Pipeline ETL, estrategia de análisis, selección de modelos y criterios de evaluación",
                           className="text-muted mb-4"),
                    width=12,
                )
            ),

            # ── Fuente de datos ──────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(html.Div([svg_icon('bank')], style={
                                            "font-size": "2.6rem",
                                            "line-height": "1",
                                            "filter": "drop-shadow(0 0 8px rgba(212,175,55,0.5))",
                                            "text-align": "center",
                                        }), width=2,
                                                className="d-flex align-items-center justify-content-center"),
                                        dbc.Col(
                                            [
                                                html.H5("Fuente de Datos",
                                                        className="fw-bold mb-2", style={"color": "#F5C842"}),
                                                html.P(
                                                    """
                                                    Banco de la República de Colombia – Sistema estadístico de
                                                    tasas de interés de colocación. Los datos están disponibles
                                                    en el portal de estadísticas del Banco de la República y
                                                    comprenden registros mensuales desde marzo de 1998 hasta
                                                    agosto de 2025 (330 observaciones).
                                                    """,
                                                    className="text-secondary mb-2",
                                                ),
                                                dbc.Row(
                                                    [
                                                        _meta_badge("Período", "Mar 1998 – Ago 2025"),
                                                        _meta_badge("Frecuencia", "Mensual"),
                                                        _meta_badge("Registros", "330 observaciones"),
                                                        _meta_badge("Variables", "7 series financieras"),
                                                        _meta_badge("Datos faltantes", "Ninguno"),
                                                        _meta_badge("Escala", "Porcentaje (%)"),
                                                    ],
                                                    className="g-2",
                                                ),
                                            ],
                                            width=10,
                                        ),
                                    ]
                                )
                            ]
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Pipeline ETL ─────────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('gear'), " Pipeline Metodológico"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        f"Fase {row['Fase']}",
                                        className="small fw-bold mb-1 px-2 py-1 rounded-pill d-inline-block",
                                        style={"background": "#D4AF37", "color": "#E8D5A3"},
                                    ),
                                    html.H6(row["Etapa"], className="fw-bold mt-2 mb-1", style={"color": "#F5C842"}),
                                    html.P(row["Descripción"], className="small text-secondary mb-2"),

                                ]
                            ),
                            className="shadow-sm border-0 h-100",
                            style={"background": row["Color"], "border-radius": "14px"},
                        ),
                        xs=12, sm=6, md=4, className="mb-3",
                    )
                    for _, row in df_pipe.iterrows()
                ]
            ),

            # ── Estrategia de modelado ───────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('robot'), " Estrategia de Modelado"],
                                        className="fw-semibold mb-3", style={"color": "#F5C842"}),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H6("Enfoque 1: ARIMA", className="fw-bold text-primary mb-2"),
                                                html.Ul(
                                                    [
                                                        html.Li("Verificación de estacionariedad (ADF/KPSS)", className="small text-secondary"),
                                                        html.Li("Identificación de parámetros via ACF/PACF", className="small text-secondary"),
                                                        html.Li("Estimación de parámetros (MLE)", className="small text-secondary"),
                                                        html.Li("Validación de residuales", className="small text-secondary"),
                                                        html.Li("Pronóstico con intervalos de confianza", className="small text-secondary"),
                                                    ]
                                                ),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.H6("Enfoque 2: Red Neuronal (LSTM)", className="fw-bold text-success mb-2"),
                                                html.Ul(
                                                    [
                                                        html.Li("Normalización y ventanas de tiempo", className="small text-secondary"),
                                                        html.Li("Arquitectura LSTM con capas densas", className="small text-secondary"),
                                                        html.Li("Ajuste de hiperparámetros", className="small text-secondary"),
                                                        html.Li("Validación cruzada temporal", className="small text-secondary"),
                                                        html.Li("Comparación de métricas MAE/RMSE", className="small text-secondary"),
                                                    ]
                                                ),
                                            ],
                                            md=6,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
        className="px-3 py-3",
    )


def _meta_badge(label, value):
    return dbc.Col(
        html.Div(
            [
                html.Span(label, className="small text-muted d-block"),
                html.Span(value, className="small fw-bold", style={"color": "#F5C842"}),
            ],
            className="px-3 py-2 rounded-3",
            style={"background": "#1C1C22", "border": "1px solid #e0e0f0"},
        ),
        xs=6, sm=4, md=2,
    )
