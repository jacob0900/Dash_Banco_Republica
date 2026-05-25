"""
tabs/prediccion.py
Pestaña 8 – Prueba de estacionariedad (ADF y KPSS).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tabs.svg_icons import svg_icon
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data.generate_data import DF
from model.train_model import load_model_results


def _acf_plot(series: pd.Series, nlags: int = 40, title: str = "ACF"):
    """Calcula y grafica la función de autocorrelación."""
    from statsmodels.tsa.stattools import acf
    acf_vals, confint = acf(series.dropna(), nlags=nlags, alpha=0.05)
    lags = list(range(len(acf_vals)))
    conf = 1.96 / np.sqrt(len(series))

    fig = go.Figure()
    fig.add_hline(y=0, line_color="#5A5A6E", line_width=1)
    fig.add_hrect(y0=-conf, y1=conf, fillcolor="rgba(212,160,23,0.12)", line_width=0)
    for lag, val in zip(lags, acf_vals):
        color = "#D4A017" if abs(val) > conf else "#3D3D4A"
        fig.add_trace(go.Bar(x=[lag], y=[val], marker_color=color, showlegend=False, width=0.6))
    fig.update_layout(
        title=title, xaxis_title=dict(text="Lag", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Autocorrelación", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40), height=280,
    )
    return fig


def _pacf_plot(series: pd.Series, nlags: int = 40, title: str = "PACF"):
    """Calcula y grafica la función de autocorrelación parcial."""
    from statsmodels.tsa.stattools import pacf
    pacf_vals = pacf(series.dropna(), nlags=nlags)
    lags = list(range(len(pacf_vals)))
    conf = 1.96 / np.sqrt(len(series))

    fig = go.Figure()
    fig.add_hline(y=0, line_color="#5A5A6E", line_width=1)
    fig.add_hrect(y0=-conf, y1=conf, fillcolor="rgba(212,160,23,0.12)", line_width=0)
    for lag, val in zip(lags, pacf_vals):
        color = "#F9E68C" if abs(val) > conf else "#2E2E38"
        fig.add_trace(go.Bar(x=[lag], y=[val], marker_color=color, showlegend=False, width=0.6))
    fig.update_layout(
        title=title, xaxis_title=dict(text="Lag", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Autocorrelación Parcial", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40), height=280,
    )
    return fig


def layout():
    df   = DF.copy()
    res  = load_model_results()
    serie = df.set_index("Fecha")["TasaColocacionTotal"]
    serie_diff = serie.diff().dropna()

    # ── ACF / PACF serie original y diferenciada
    fig_acf_orig   = _acf_plot(serie,      title="ACF – Serie Original")
    fig_pacf_orig  = _pacf_plot(serie,     title="PACF – Serie Original")
    fig_acf_diff   = _acf_plot(serie_diff, title="ACF – Primera Diferencia")
    fig_pacf_diff  = _pacf_plot(serie_diff,title="PACF – Primera Diferencia")

    # ── Serie temporal + primera diferencia
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=serie.index, y=serie.values, mode="lines",
                                name="Serie Original", line=dict(color="#D4A017", width=1.8)))
    fig_ts.update_layout(title=dict(text="Serie Original: Tasa de Colocación Total", font=dict(color="#F5C842", size=14)),
                         xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
                         paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
                         margin=dict(l=40, r=20, t=50, b=40), height=260)

    fig_diff = go.Figure()
    fig_diff.add_trace(go.Scatter(x=serie_diff.index, y=serie_diff.values, mode="lines",
                                  name="Primera Diferencia", line=dict(color="#C8963C", width=1.8)))
    fig_diff.add_hline(y=0, line_dash="dash", line_color="#5A5A6E")
    fig_diff.update_layout(title=dict(text="Primera Diferencia (d=1)", font=dict(color="#F5C842", size=14)),
                           xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Δ Tasa (%)", font=dict(color="#CEC5A8")),
                           paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
                           margin=dict(l=40, r=20, t=50, b=40), height=260)

    adf_orig  = res["serie_original"]["adf"]
    kpss_orig = res["serie_original"]["kpss"]
    adf_diff  = res["primera_diferencia"]["adf"]
    kpss_diff = res["primera_diferencia"]["kpss"]

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H3("Prueba de Estacionariedad",
                            className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Tests ADF y KPSS aplicados a la Tasa de Colocación Total y su primera diferencia",
                           className="text-muted mb-4"),
                    width=12,
                )
            ),

            # ── ¿Qué es estacionariedad? ─────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('info'), " ¿Por qué importa la estacionariedad?"],
                                        className="fw-semibold mb-3", style={"color": "#F5C842"}),
                                html.P(
                                    """
                                    Un proceso estacionario tiene media, varianza y autocovarianza
                                    constantes en el tiempo. Esta propiedad es esencial para que los
                                    modelos ARIMA sean válidos: si la serie no es estacionaria, los
                                    parámetros estimados son inconsistentes y las predicciones no son
                                    confiables. La estacionariedad se verifica con pruebas estadísticas
                                    formales antes de cualquier modelado.
                                    """,
                                    className="text-secondary mb-0",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Series temporales ────────────────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(dcc.Graph(figure=fig_ts, config={"displayModeBar": False})),
                            className="shadow-sm border-0",
                            style={"border-radius": "14px"},
                        ),
                        md=6, className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(dcc.Graph(figure=fig_diff, config={"displayModeBar": False})),
                            className="shadow-sm border-0",
                            style={"border-radius": "14px"},
                        ),
                        md=6, className="mb-4",
                    ),
                ]
            ),

            # ── Resultados ADF ───────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('microscope'), " Test ADF (Augmented Dickey-Fuller)"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                [
                    _test_card("Serie Original", adf_orig, "#ffffff"),
                    _test_card("Primera Diferencia (d=1)", adf_diff, "#ffffff"),
                ],
                className="g-3 mb-4",
            ),

            # ── Resultados KPSS ──────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('microscope'), " Test KPSS (Kwiatkowski-Phillips-Schmidt-Shin)"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                [
                    _test_card("Serie Original", kpss_orig, "#ffffff"),
                    _test_card("Primera Diferencia (d=1)", kpss_diff, "#ffffff"),
                ],
                className="g-3 mb-4",
            ),

            # ── Interpretación conjunta ──────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('pin'), " Interpretación Conjunta ADF + KPSS"],
                                        className="fw-semibold mb-2", style={"color": "#F5C842"}),
                                html.P(res["interpretacion_conjunta"],
                                       className="text-secondary mb-0 fw-semibold"),
                            ]
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#f5f0ff", "border-radius": "14px",
                               "border-left": "5px solid #000000"},
                    ),
                    width=12,
                )
            ),

            # ── Próximos pasos ───────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('rocket'), " Próximos Pasos"],
                                        className="fw-semibold mb-3", style={"color": "#F5C842"}),
                                dbc.Row(
                                    [
                                        _paso_item("1", "Identificación ARIMA",
                                                   "Con base en los resultados de ACF y PACF, "
                                                   "determinar los parámetros óptimos (p, d, q)."),
                                        _paso_item("2", "Estimación del Modelo",
                                                   "Ajustar el modelo ARIMA y evaluar la bondad "
                                                   "de ajuste con AIC y BIC."),
                                        _paso_item("3", "Validación de Residuales",
                                                   "Verificar que los residuales sean ruido blanco "
                                                   "(normalidad e independencia)."),
                                        _paso_item("4", "Pronóstico",
                                                   "Generar proyecciones con intervalos de confianza "
                                                   "para los próximos períodos."),
                                    ],
                                    className="g-3",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                        style={"background": "#f8f9ff", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
        className="px-3 py-3",
    )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _test_card(titulo: str, result: dict, bg: str):
    from tabs.svg_icons import svg_icon as _svg
    icono = _svg('check_circle', color='#4caf7d') if result["es_estacionaria"] else _svg('warning', color='#d4a04a')
    pval_color = "#000000" if result["es_estacionaria"] else "#dc3545"
    crit_vals = result.get("valores_criticos", {})

    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6([icono, f" {titulo}"], className="fw-bold mb-3", style={"color": "#F5C842"}),
                    dbc.Row(
                        [
                            dbc.Col([
                                html.P("Estadístico", className="small text-muted mb-0"),
                                html.H5(f"{result['estadistico']:.4f}", className="fw-bold mb-0",
                                        style={"color": "#F5C842"}),
                            ], width=6),
                            dbc.Col([
                                html.P("p-valor", className="small text-muted mb-0"),
                                html.H5(f"{result['p_value']:.4f}", className="fw-bold mb-0",
                                        style={"color": pval_color}),
                            ], width=6),
                        ],
                        className="mb-3",
                    ),
                    html.P("Valores Críticos:", className="small text-muted mb-1"),
                    html.Div(
                        [
                            html.Span(
                                f"{k}: {v}  ",
                                className="small me-2 px-2 py-1 rounded",
                                style={"background": "#1C1C22", "font-size": "0.75rem"},
                            )
                            for k, v in crit_vals.items()
                        ],
                        className="mb-3",
                    ),
                    html.Hr(className="my-2"),
                    html.P(result["hipotesis_nula"],
                           className="small text-muted fst-italic mb-2"),
                    html.P(result["conclusion"],
                           className="small fw-semibold mb-0",
                           style={"color": pval_color}),
                ]
            ),
            className="shadow-sm border-0 h-100",
            style={"background": "#1C1C22", "border-radius": "14px"},
        ),
        md=6,
    )


def _paso_item(num, titulo, desc):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        num,
                        className="rounded-circle fw-bold text-white d-flex align-items-center "
                                  "justify-content-center mb-2 mx-auto",
                        style={"width": "32px", "height": "32px",
                               "background": "#1C1C22", "font-size": "0.9rem"},
                    ),
                    html.H6(titulo, className="fw-bold text-center mb-2", style={"color": "#F5C842"}),
                    html.P(desc, className="small text-secondary text-center mb-0"),
                ]
            ),
            className="border-0 text-center",
            style={"background": "#f8f6ff", "border-radius": "12px"},
        ),
        xs=12, sm=6, md=3,
    )
