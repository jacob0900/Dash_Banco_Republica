"""
tabs/marco_teorico.py
Pestaña 5 – Marco teórico e tabla de operacionalización de variables.
"""

from tabs.svg_icons import svg_icon
from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd


# Tabla de operacionalización de variables
OPERACIONALIZACION = pd.DataFrame(
    {
        "Variable": [
            "Fecha",
            "Créditos de Consumo",
            "Créditos de Tesorería",
            "Créditos Ordinarios",
            "Créditos Preferenciales",
            "Tasa Colocación BR",
            "Tasa Colocación Sin Tesorería",
            "Tasa Colocación Total",
        ],
        "Tipo": [
            "Temporal",
            "Numérica continua",
            "Numérica continua",
            "Numérica continua",
            "Numérica continua",
            "Numérica continua",
            "Numérica continua",
            "Numérica continua",
        ],
        "Definición Conceptual": [
            "Fecha de registro mensual de la serie",
            "Tasa de créditos otorgados para financiar bienes y servicios de consumo de personas naturales",
            "Tasa de créditos de corto plazo para necesidades de liquidez empresarial",
            "Tasa de créditos comerciales estándar para actividades productivas",
            "Tasa de créditos a condiciones favorables para empresas de bajo riesgo",
            "Tasa de colocación de referencia fijada por el Banco de la República",
            "Tasa de colocación del sistema excluyendo la modalidad de tesorería",
            "Tasa de colocación promedio ponderado de todo el sistema financiero",
        ],
        "Escala de Medición": [
            "Intervalo",
            "Razón",
            "Razón",
            "Razón",
            "Razón",
            "Razón",
            "Razón",
            "Razón",
        ],
        "Unidad": [
            "Fecha (AAAA-MM-DD)",
            "Porcentaje (%)",
            "Porcentaje (%)",
            "Porcentaje (%)",
            "Porcentaje (%)",
            "Porcentaje (%)",
            "Porcentaje (%)",
            "Porcentaje (%)",
        ],
        "Rol en el Análisis": [
            "Variable de índice temporal",
            "Variable predictora",
            "Variable predictora",
            "Variable predictora",
            "Variable predictora",
            "Variable predictora",
            "Variable predictora",
            "Variable objetivo (target)",
        ],
    }
)


def layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H3("Marco Teórico",
                            className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Fundamentos conceptuales, modelos de series de tiempo y operacionalización de variables",
                           className="text-muted mb-4"),
                    width=12,
                )
            ),

            # ── Conceptos clave ─────────────────────────────────────────────
            dbc.Row(
                [
                    _concepto_card(svg_icon('trending_up'), "Series de Tiempo",
                                   "Secuencia de observaciones indexadas cronológicamente. "
                                   "Su análisis busca identificar tendencia, estacionalidad, "
                                   "ciclicidad y ruido aleatorio (Box & Jenkins, 1976).", "#dce8ff"),
                    _concepto_card(svg_icon('scale'), "Estacionariedad",
                                   "Una serie es estacionaria si su media, varianza y autocovarianza "
                                   "son constantes en el tiempo. Condición necesaria para muchos "
                                   "modelos econométricos.", "#2E2E38"),
                    _concepto_card(svg_icon('database'), "Modelo ARIMA",
                                   "AutoRegressive Integrated Moving Average. Combina autorregresión (AR), "
                                   "diferenciación (I) y media móvil (MA) para modelar series temporales "
                                   "estacionarias o estacionarizadas.", "#fff4dc"),
                    _concepto_card(svg_icon('brain'), "Redes Neuronales",
                                   "Modelos de aprendizaje automático capaces de capturar relaciones "
                                   "no lineales en los datos. Las arquitecturas LSTM son especialmente "
                                   "adecuadas para series de tiempo.", "#fde8e8"),
                ],
                className="g-3 mb-4",
            ),

            # ── Pruebas de estacionariedad ───────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('microscope'), " Pruebas de Estacionariedad"],
                                        className="fw-semibold mb-3", style={"color": "#F5C842"}),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H6("Prueba ADF (Augmented Dickey-Fuller)",
                                                        className="fw-bold text-primary mb-2"),
                                                html.P("H₀: La serie tiene raíz unitaria (no es estacionaria)",
                                                       className="small text-secondary mb-1"),
                                                html.P("H₁: La serie es estacionaria",
                                                       className="small text-secondary mb-1"),
                                                html.P("Se rechaza H₀ si p-valor < 0.05",
                                                       className="small text-muted fst-italic"),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.H6("Prueba KPSS (Kwiatkowski-Phillips-Schmidt-Shin)",
                                                        className="fw-bold text-success mb-2"),
                                                html.P("H₀: La serie es estacionaria",
                                                       className="small text-secondary mb-1"),
                                                html.P("H₁: La serie tiene raíz unitaria",
                                                       className="small text-secondary mb-1"),
                                                html.P("Se rechaza H₀ si p-valor < 0.05",
                                                       className="small text-muted fst-italic"),
                                            ],
                                            md=6,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Métricas de evaluación ───────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('ruler'), " Métricas de Evaluación"],
                                        className="fw-semibold mb-3", style={"color": "#F5C842"}),
                                dbc.Row(
                                    [
                                        _metrica_card("MAE", "Error Absoluto Medio",
                                                      "Promedio de las diferencias absolutas entre valores reales y predichos."),
                                        _metrica_card("RMSE", "Raíz del Error Cuadrático Medio",
                                                      "Penaliza errores grandes con mayor peso que el MAE."),
                                        _metrica_card("AIC", "Criterio de Información de Akaike",
                                                      "Mide la bondad de ajuste penalizando la complejidad del modelo."),
                                        _metrica_card("BIC", "Criterio de Información Bayesiano",
                                                      "Similar al AIC pero con penalización más fuerte por parámetros adicionales."),
                                    ],
                                    className="g-2",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Tabla de operacionalización ──────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('clipboard'), " Tabla de Operacionalización de Variables"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                data=OPERACIONALIZACION.to_dict("records"),
                                columns=[{"name": c, "id": c} for c in OPERACIONALIZACION.columns],
                                style_table={"overflowX": "auto"},
                                style_header={
                                    "backgroundColor": "#1A1A22",
                                    "color": "#E8D5A3",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "fontSize": "13px",
                                    "padding": "10px",
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"row_index": "odd"},
                                        "backgroundColor": "#ffffff",
                                    },
                                    {
                                        "if": {"column_id": "Variable"},
                                        "fontWeight": "bold",
                                        "color": "#E8D5A3",
                                    },
                                    {
                                        "if": {"filter_query": '{Rol en el Análisis} = "Variable objetivo (target)"'},
                                        "backgroundColor": "#f5f5f5",
                                        "fontWeight": "bold",
                                    },
                                ],
                                style_cell={
                                    "textAlign": "left",
                                    "padding": "10px 14px",
                                    "fontSize": "12px",
                                    "fontFamily": "Inter, sans-serif",
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                page_action="none",
                            )
                        ),
                        className="shadow-sm border-0",
                        style={"border-radius": "14px"},
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
        className="px-3 py-3",
    )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _concepto_card(icon, title, desc, bg):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(icon, style={
                        "font-size": "2.4rem",
                        "line-height": "1",
                        "margin-bottom": "12px",
                        "filter": "drop-shadow(0 0 8px rgba(212,175,55,0.5))",
                        "display": "block",
                    }),
                    html.H6(title, className="fw-bold mb-2", style={"color": "#F5C842"}),
                    html.P(desc, className="small text-secondary mb-0"),
                ]
            ),
            className="shadow-sm border-0 h-100",
            style={
                "background": "#1C1C22",
                "border-radius": "14px",
                "border-top": "2px solid #3D2E0A !important",
                "transition": "border-color 0.2s",
            },
        ),
        xs=12, sm=6, md=3,
    )


def _metrica_card(acronimo, nombre, desc):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5(acronimo, className="fw-bold mb-1", style={"color": "#F5C842"}),
                    html.P(nombre, className="small fw-semibold mb-1", style={"color": "#F5C842"}),
                    html.P(desc, className="small text-secondary mb-0"),
                ]
            ),
            className="border-0",
            style={"background": "#141418", "border-radius": "10px"},
        ),
        xs=12, sm=6, md=3,
    )
