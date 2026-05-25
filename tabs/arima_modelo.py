"""
tabs/arima_modelo.py
Pestaña – Modelo ARIMA: ACF/PACF, selección de parámetros, pronóstico y métricas de error.
Refleja los análisis del notebook EdaVis.ipynb (Celdas 73-87) con interpretaciones detalladas del VisBook.
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


# ── Paleta Obsidian Gold ────────────────────────────────────────────────────
COLOR_TRAIN  = "#D4A017"
COLOR_TEST   = "#CEC5A8"
COLOR_PRED   = "#F5C842"
COLOR_CI     = "rgba(212, 160, 23, 0.12)"
COLOR_CARD   = "#1C1C22"
COLOR_SIG    = "#D4A017"
COLOR_NONSIG = "#3D3D4A"
RADIUS       = "14px"


# ── ACF / PACF Figures ─────────────────────────────────────────────────────

def _acf_figure(serie, nlags=40, title="ACF"):
    from statsmodels.tsa.stattools import acf
    vals_clean = serie.dropna()
    acf_vals, confint = acf(vals_clean, nlags=nlags, alpha=0.05)
    lags = list(range(len(acf_vals)))
    conf = 1.96 / np.sqrt(len(vals_clean))

    fig = go.Figure()
    fig.add_hline(y=0, line_color="#5A5A6E", line_width=1)
    fig.add_hrect(y0=-conf, y1=conf, fillcolor="rgba(212,160,23,0.12)", line_width=0)

    for lag, val in zip(lags, acf_vals):
        color = COLOR_SIG if (abs(val) > conf and lag > 0) else COLOR_NONSIG
        fig.add_trace(go.Bar(x=[lag], y=[val], marker_color=color,
                             showlegend=False, width=0.6,
                             hovertemplate=f"Lag {lag}<br>ACF = {val:.4f}<extra></extra>"))

    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#F4EED8"), x=0.5, xanchor="center"),
        xaxis_title=dict(text="Lag", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Autocorrelación", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        xaxis=dict(color="#8A8272", gridcolor="#2E2E38"),
        yaxis=dict(color="#8A8272", gridcolor="#2E2E38"),
        margin=dict(l=50, r=20, t=55, b=45), height=300,
        font=dict(family="Jost, sans-serif", size=11, color="#CEC5A8"),
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )
    return fig


def _pacf_figure(serie, nlags=40, title="PACF"):
    from statsmodels.tsa.stattools import pacf
    vals_clean = serie.dropna()
    max_lags = min(nlags, len(vals_clean) // 2 - 1)
    pacf_vals = pacf(vals_clean, nlags=max_lags, method="ywm")
    lags = list(range(len(pacf_vals)))
    conf = 1.96 / np.sqrt(len(vals_clean))

    fig = go.Figure()
    fig.add_hline(y=0, line_color="#5A5A6E", line_width=1)
    fig.add_hrect(y0=-conf, y1=conf, fillcolor="rgba(212,160,23,0.08)", line_width=0)

    for lag, val in zip(lags, pacf_vals):
        color = COLOR_SIG if (abs(val) > conf and lag > 0) else COLOR_NONSIG
        fig.add_trace(go.Bar(x=[lag], y=[val], marker_color=color,
                             showlegend=False, width=0.6,
                             hovertemplate=f"Lag {lag}<br>PACF = {val:.4f}<extra></extra>"))

    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#F4EED8"), x=0.5, xanchor="center"),
        xaxis_title=dict(text="Lag", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Autocorrelación Parcial", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        xaxis=dict(color="#8A8272", gridcolor="#2E2E38"),
        yaxis=dict(color="#8A8272", gridcolor="#2E2E38"),
        margin=dict(l=50, r=20, t=55, b=45), height=300,
        font=dict(family="Jost, sans-serif", size=11, color="#CEC5A8"),
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )
    return fig


def _param_badge(param, label, color, descripcion):
    return dbc.Card(
        dbc.CardBody([
            html.H4(param, className="fw-bold mb-0", style={"color": color, "font-size": "1.8rem"}),
            html.P(label, className="small fw-semibold text-muted mb-2"),
            html.P(descripcion, className="small text-secondary mb-0",
                   style={"font-size": "0.78rem", "text-align": "justify"}),
        ]),
        className="shadow-sm border-0 h-100 text-center",
        style={"background": "#1C1C22", "border-radius": RADIUS,
               "border-top": f"4px solid {color}"},
    )


def _acf_pacf_section(serie):
    serie_diff = serie.diff().dropna()

    fig_acf_orig  = _acf_figure(serie,       nlags=40, title="ACF – Serie Original")
    fig_pacf_orig = _pacf_figure(serie,      nlags=40, title="PACF – Serie Original")
    fig_acf_diff  = _acf_figure(serie_diff,  nlags=40, title="ACF – Primera Diferencia")
    fig_pacf_diff = _pacf_figure(serie_diff, nlags=40, title="PACF – Primera Diferencia")

    return [
        dbc.Row(dbc.Col(
            html.H4([svg_icon('trending_down'), " Función de Autocorrelación (ACF) y Autocorrelación Parcial (PACF)"],
                    className="fw-bold mb-1 mt-2", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            html.P(
                "Identificación visual de los parámetros p y q del modelo ARIMA a partir de "
                "los correlogramas de la serie original y su primera diferencia.",
                className="text-muted mb-3",
            ),
            width=12,
        )),

        # Conceptual block
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6([svg_icon('pin'), " ¿Qué es la ACF?"], className="fw-bold mb-2",
                                    style={"color": "#D4A017"}),
                            html.P(
                                "La Función de Autocorrelación (ACF) mide la correlación entre "
                                "la serie y sus propios rezagos (lags). Un decaimiento lento y "
                                "progresivo en la ACF indica no estacionariedad. Una vez diferenciada "
                                "la serie, el número de lags significativos que quedan fuera de las "
                                "bandas de confianza sugiere el orden del componente MA(q).",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ], md=6),
                        dbc.Col([
                            html.H6([svg_icon('pin'), " ¿Qué es la PACF?"], className="fw-bold mb-2",
                                    style={"color": "#E8A020"}),
                            html.P(
                                "La Función de Autocorrelación Parcial (PACF) mide la correlación "
                                "entre la serie y un rezago específico, eliminando el efecto de los "
                                "rezagos intermedios. Tras la diferenciación, el número de lags "
                                "significativos indica el orden del componente AR(p). Un corte abrupto "
                                "en la PACF sugiere un modelo AR puro.",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ], md=6),
                    ]),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#f8f6ff", "border-radius": RADIUS,
                       "border-left": "5px solid #7b6cf7"},
            ),
            width=12,
        )),

        # Serie original charts
        dbc.Row(dbc.Col(
            html.H5("Serie Original — TasaColocacionTotal",
                    className="fw-semibold mb-2", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_acf_orig, config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_pacf_orig, config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-3",
            ),
        ]),

        # Interpretation original
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6([svg_icon('search'), " Interpretación — Serie Original"],
                            className="fw-bold mb-2", style={"color": "#F5C842"}),
                    dbc.Row([
                        dbc.Col([
                            html.Span("ACF — Serie Original", className="small fw-semibold d-block mb-1",
                                      style={"color": "#D4A017"}),
                            html.P(
                                "La ACF de la serie original muestra un decaimiento muy lento y "
                                "progresivo, con rezagos altamente significativos que permanecen "
                                "por encima de las bandas de confianza durante muchos periodos. "
                                "Este patrón es la firma característica de una serie no estacionaria "
                                "con tendencia: la alta correlación en los primeros lags refleja que "
                                "los valores pasados siguen influyendo de manera prolongada sobre los "
                                "presentes. Este comportamiento confirma que la serie necesita "
                                "diferenciación antes de aplicar el modelo ARIMA.",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ], md=6),
                        dbc.Col([
                            html.Span("PACF — Serie Original", className="small fw-semibold d-block mb-1",
                                      style={"color": "#E8A020"}),
                            html.P(
                                "La PACF de la serie original presenta un pico muy pronunciado en el "
                                "lag 1, que supera ampliamente las bandas de confianza, seguido de un "
                                "decaimiento rápido hacia valores no significativos. Este patrón sugiere "
                                "que la mayor parte de la dependencia temporal se concentra en un único "
                                "rezago, lo que es consistente con la presencia de una raíz unitaria. "
                                "En combinación con la ACF, indica que la serie no es estacionaria "
                                "y que se requiere diferenciación de primer orden (d = 1).",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ], md=6),
                    ]),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#1C1C22", "border-radius": RADIUS,
                       "border-top": "3px solid #e8e4ff"},
            ),
            width=12,
        )),

        # Primera diferencia charts
        dbc.Row(dbc.Col(
            html.H5("Primera Diferencia — TasaColocacionTotal (Δ¹)",
                    className="fw-semibold mb-2", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_acf_diff, config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_pacf_diff, config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-3",
            ),
        ]),

        # Interpretation primera diferencia
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6([svg_icon('search'), " Interpretación — Primera Diferencia (d = 1)"],
                            className="fw-bold mb-2", style={"color": "#F5C842"}),
                    dbc.Row([
                        dbc.Col([
                            html.Span("ACF — Primera Diferencia", className="small fw-semibold d-block mb-1",
                                      style={"color": "#D4A017"}),
                            html.P(
                                "Tras aplicar la primera diferencia, la ACF cambia radicalmente: "
                                "la mayoría de los rezagos caen dentro de las bandas de confianza, "
                                "lo que confirma que la diferenciación logró estabilizar la media y "
                                "eliminar la tendencia. Los rezagos significativos que permanecen "
                                "fuera de las bandas (principalmente los primeros 1-3 lags) indican "
                                "el orden del componente de media móvil q del modelo ARIMA. Se observan "
                                "hasta 3 rezagos significativos, lo que sugiere q = 3 como candidato, "
                                "coherente con el modelo ARIMA(0,1,3) seleccionado por Grid Search AIC.",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ], md=6),
                        dbc.Col([
                            html.Span("PACF — Primera Diferencia", className="small fw-semibold d-block mb-1",
                                      style={"color": "#E8A020"}),
                            html.P(
                                "La PACF de la primera diferencia muestra que los rezagos caen "
                                "rápidamente dentro de las bandas de confianza, sin picos prolongados "
                                "fuera del IC. Este comportamiento indica que no hay dependencia AR "
                                "significativa en la serie diferenciada, lo cual es consistente con "
                                "un componente autorregresivo de orden p = 0. En combinación con la "
                                "ACF, estos gráficos confirman modelos del tipo ARIMA(0,1,q), siendo "
                                "ARIMA(0,1,1) o ARIMA(0,1,3) los candidatos más fuertes, confirmados "
                                "posteriormente por el criterio AIC.",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ], md=6),
                    ]),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#1C1C22", "border-radius": RADIUS,
                       "border-top": "3px solid #d0eaf8"},
            ),
            width=12,
        )),

        # Conclusión ACF/PACF
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5([svg_icon('check_circle', color='#4caf7d'), " Conclusión del Análisis ACF/PACF → Fijación de d = 1"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    dbc.Row([
                        dbc.Col(_param_badge("d = 1", "Diferenciación", "#27ae60",
                            "La primera diferencia logra estabilizar la serie. "
                            "Las pruebas ADF y KPSS en la serie diferenciada confirman estacionariedad."),
                            md=4, className="mb-3"),
                        dbc.Col(_param_badge("p = 0", "Componente AR", "#D4A017",
                            "La PACF de la serie diferenciada no presenta rezagos significativos, "
                            "indicando que no se necesita componente autorregresivo."),
                            md=4, className="mb-3"),
                        dbc.Col(_param_badge("q = 1–3", "Componente MA", "#e67e22",
                            "La ACF de la serie diferenciada muestra hasta 3 rezagos significativos. "
                            "El Grid Search AIC confirma q = 3 como óptimo."),
                            md=4, className="mb-3"),
                    ]),
                    html.Hr(className="my-2"),
                    html.P(
                        "Al verificar que la primera diferencia vuelve estacionaria la serie, se fija "
                        "el parámetro d = 1 en el modelo ARIMA. Los gráficos ACF y PACF muestran que los "
                        "rezagos significativos se concentran en los primeros lags (principalmente en la ACF), "
                        "lo que sugiere modelos del tipo ARIMA(0,1,1) como fuertes candidatos iniciales. "
                        "La estimación robusta de los parámetros p y q se completa mediante Grid Search con "
                        "criterio AIC, que selecciona finalmente ARIMA(0,1,3) como el modelo óptimo.",
                        className="small text-secondary mb-0",
                        style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0 mb-5",
                style={"background": "#f0fff4", "border-radius": RADIUS,
                       "border-left": "5px solid #27ae60"},
            ),
            width=12,
        )),
    ]


def _forecast_figure(res):
    arima = res.get("arima", {})
    train_idx  = pd.to_datetime(arima.get("train_index", []))
    test_idx   = pd.to_datetime(arima.get("test_index",  []))
    train_vals = arima.get("train_values", [])
    test_vals  = arima.get("test_values",  [])
    pred_vals  = arima.get("pred_mean",    [])
    ci_lower   = arima.get("ci_lower",     [])
    ci_upper   = arima.get("ci_upper",     [])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_idx, y=train_vals, mode="lines",
        name="Entrenamiento (80 %)", line=dict(color=COLOR_TRAIN, width=1.8)))
    fig.add_trace(go.Scatter(x=test_idx, y=test_vals, mode="lines",
        name="Valores Reales (Prueba 20 %)", line=dict(color=COLOR_TEST, width=1.8)))
    fig.add_trace(go.Scatter(
        x=list(test_idx) + list(test_idx[::-1]),
        y=list(ci_upper) + list(reversed(ci_lower)),
        fill="toself", fillcolor=COLOR_CI, line=dict(color="rgba(0,0,0,0)"),
        name="Intervalo de Confianza 95 %", showlegend=True))
    fig.add_trace(go.Scatter(x=test_idx, y=pred_vals, mode="lines",
        name=f"Predicción {arima.get('order_str','ARIMA')}",
        line=dict(color=COLOR_PRED, width=2, dash="dash")))

    fig.update_layout(
        title=f"Pronóstico {arima.get('order_str','ARIMA')} – Tasa de Colocación Total",
        xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        xaxis=dict(color="#8A8272", gridcolor="#2E2E38"),
        yaxis=dict(color="#8A8272", gridcolor="#2E2E38"),
        font=dict(family="Jost, sans-serif", size=11, color="#CEC5A8"),
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(color="#CEC5A8")),
        margin=dict(l=50, r=20, t=55, b=60), height=380,
    )
    return fig


def _metrics_row(arima):
    metrics = [
        ("MAE",  arima.get("mae",  "–"), "Error Absoluto Medio",        "#D4A017"),
        ("RMSE", arima.get("rmse", "–"), "Raíz del Error Cuadrático",   "#F9E68C"),
        ("MAPE", f"{arima.get('mape', '–')} %", "Error Porcentual Medio", "#F9E79F"),
        ("R²",   arima.get("r2",   "–"), "Coeficiente de Determinación","#C8963C"),
        ("AIC",  arima.get("aic",  "–"), "Criterio de Info. Akaike",    "#E8A020"),
        ("BIC",  arima.get("bic",  "–"), "Criterio de Info. Bayesiano", "#FADBD8"),
    ]
    cols = []
    for label, value, desc, color in metrics:
        cols.append(dbc.Col(
            dbc.Card(dbc.CardBody([
                html.P(label, className="small fw-bold text-muted mb-1",
                       style={"letter-spacing": "0.5px"}),
                html.H4(str(round(value, 4)) if isinstance(value, float) else str(value),
                        className="fw-bold mb-0", style={"color": "#1a1a2e", "font-size": "1.4rem"}),
                html.P(desc, className="small text-muted mt-1 mb-0", style={"font-size": "0.72rem"}),
            ]),
                className="shadow-sm border-0 h-100",
                style={"border-radius": RADIUS, "background": COLOR_CARD,
                       "border-top": f"4px solid {color}"},
            ),
            xs=6, sm=4, md=2, className="mb-3",
        ))
    return dbc.Row(cols, className="g-2")


def _grid_search_card(arima):
    return dbc.Card(
        dbc.CardBody([
            html.H5([svg_icon('search'), " Selección de Parámetros — Grid Search AIC"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            html.P(
                "Se evaluaron todas las combinaciones (p, d, q) con p ∈ [0,3], d ∈ [0,1], "
                "q ∈ [0,3] sobre el 80 % de entrenamiento. El modelo con menor AIC fue "
                "seleccionado como candidato óptimo.",
                className="text-secondary mb-3",
            ),
            dbc.Row([
                dbc.Col([html.P("Mejor Orden", className="small text-muted mb-0"),
                         html.H4(arima.get("order_str", "–"), className="fw-bold",
                                 style={"color": "#D4A017"})], xs=6, md=3),
                dbc.Col([html.P("AIC mínimo", className="small text-muted mb-0"),
                         html.H4(str(round(arima["aic"], 2)) if isinstance(arima.get("aic"), float) else "–",
                                 className="fw-bold", style={"color": "#1a1a2e"})], xs=6, md=3),
                dbc.Col([html.P("Obs. entrenamiento", className="small text-muted mb-0"),
                         html.H4(str(arima.get("n_train", "–")), className="fw-bold",
                                 style={"color": "#1a1a2e"})], xs=6, md=3),
                dbc.Col([html.P("Obs. prueba", className="small text-muted mb-0"),
                         html.H4(str(arima.get("n_test", "–")), className="fw-bold",
                                 style={"color": "#1a1a2e"})], xs=6, md=3),
            ]),
        ]),
        className="shadow-sm border-0 mb-4",
        style={"background": "#f8f6ff", "border-radius": RADIUS,
               "border-left": "5px solid #7b6cf7"},
    )


def _interpretation_card(arima):
    order = arima.get("order_str", "ARIMA(p,d,q)")
    mae   = arima.get("mae",  None)
    mape  = arima.get("mape", None)
    r2    = arima.get("r2",   None)

    interp = (
        f"El modelo {order}, estimado por máxima verosimilitud, describe la dinámica general "
        f"de la Tasa de Colocación Total mediante diferenciación de primer orden (d=1), lo que "
        f"confirma la no estacionariedad original de la serie. "
    )
    if mae is not None:
        interp += (
            f"Las métricas de validación sobre el conjunto de prueba muestran un MAE de "
            f"{round(mae, 4):.4f} y un MAPE de {round(mape, 2):.2f} %, lo que indica que las "
            f"predicciones puntuales tienen un error porcentual moderado-alto. "
        )
    if r2 is not None and r2 < 0:
        interp += (
            "El R² negativo refleja que el modelo no supera en rendimiento a una simple predicción "
            "con la media, lo cual es esperado en series financieras con alta volatilidad. "
            "El gráfico muestra que la predicción tiende a suavizarse frente a fluctuaciones "
            "abruptas en los datos reales. Se recomienda explorar modelos más flexibles como "
            "Máquinas de Soporte Vectorial (SVM) o redes neuronales para mejorar el ajuste."
        )
    elif r2 is not None:
        interp += (
            f"El R² de {round(r2, 4):.4f} indica que el modelo explica una parte razonable de la "
            "variabilidad de la serie en el conjunto de prueba."
        )

    return dbc.Card(
        dbc.CardBody([
            html.H5([svg_icon('pin'), " Interpretación del Modelo"], className="fw-semibold mb-2",
                    style={"color": "#F5C842"}),
            html.P(interp, className="text-secondary mb-0", style={"text-align": "justify"}),
        ]),
        className="shadow-sm border-0 mb-4",
        style={"background": "#fff9f0", "border-radius": RADIUS,
               "border-left": "5px solid #e67e22"},
    )


def layout():
    df    = DF.copy()
    res   = load_model_results()
    arima = res.get("arima", {})

    serie = df.set_index("Fecha")["TasaColocacionTotal"]
    fig_forecast = _forecast_figure(res)

    return dbc.Container([

        dbc.Row(dbc.Col(
            html.H3("Modelo ARIMA – Identificación, Estimación y Pronóstico",
                    className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            html.P(
                "ACF · PACF · Prueba de estacionariedad · Grid Search AIC · "
                "Pronóstico sobre el 20 % de prueba · Métricas MAE, RMSE, MAPE, R²",
                className="text-muted mb-4",
            ),
            width=12,
        )),

        # Info block
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5([svg_icon('info'), " ¿Qué es un modelo ARIMA?"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    html.P(
                        "ARIMA (AutoRegressive Integrated Moving Average) combina tres componentes: "
                        "AR(p) — regresión sobre p rezagos propios; I(d) — diferenciación d veces "
                        "para lograr estacionariedad; MA(q) — media móvil sobre q errores pasados. "
                        "El orden óptimo (p, d, q) se selecciona minimizando el criterio de "
                        "información de Akaike (AIC) mediante búsqueda exhaustiva. La identificación "
                        "visual de p y q se realiza mediante los correlogramas ACF y PACF.",
                        className="text-secondary mb-0", style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#1C1C22", "border-radius": RADIUS},
            ),
            width=12,
        )),

        # ACF/PACF section
        *_acf_pacf_section(serie),

        # ARIMA estimation
        dbc.Row(dbc.Col(
            html.H4([svg_icon('robot'), " Estimación del Modelo ARIMA"],
                    className="fw-bold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row(dbc.Col(_grid_search_card(arima), width=12)),

        dbc.Row(dbc.Col(
            html.H5([svg_icon('bar_chart'), " Métricas de Error – Conjunto de Prueba"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        _metrics_row(arima),

        # Metrics interpretation
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6([svg_icon('search'), " Interpretación de las Métricas"],
                            className="fw-bold mb-2", style={"color": "#F5C842"}),
                    dbc.Row([
                        dbc.Col([
                            html.Span("MAE y RMSE", className="small fw-semibold d-block mb-1",
                                      style={"color": "#D4A017"}),
                            html.P(
                                "El Error Absoluto Medio (MAE) y la Raíz del Error Cuadrático Medio (RMSE) "
                                "miden el promedio de los errores en las mismas unidades que la serie (%). "
                                "El RMSE penaliza más los errores grandes. Valores más bajos indican mejor ajuste.",
                                className="small text-secondary mb-0", style={"text-align": "justify"},
                            ),
                        ], md=4),
                        dbc.Col([
                            html.Span("MAPE", className="small fw-semibold d-block mb-1",
                                      style={"color": "#E8A020"}),
                            html.P(
                                "El Error Porcentual Absoluto Medio (MAPE) expresa el error como "
                                "porcentaje del valor real. Un MAPE elevado en series financieras "
                                "es común dada la alta volatilidad. Valores por encima del 20% "
                                "indican capacidad predictiva puntual limitada.",
                                className="small text-secondary mb-0", style={"text-align": "justify"},
                            ),
                        ], md=4),
                        dbc.Col([
                            html.Span("AIC / BIC", className="small fw-semibold d-block mb-1",
                                      style={"color": "#8BC89A"}),
                            html.P(
                                "El AIC y BIC son criterios de información que penalizan la complejidad "
                                "del modelo. Menor AIC/BIC indica mejor balance entre ajuste y parsimonia. "
                                "Son la base del Grid Search para seleccionar el orden óptimo (p, d, q).",
                                className="small text-secondary mb-0", style={"text-align": "justify"},
                            ),
                        ], md=4),
                    ]),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#1C1C22", "border-radius": RADIUS,
                       "border-top": "3px solid #e8e4ff"},
            ),
            width=12,
        )),

        # Forecast chart
        dbc.Row(dbc.Col(
            html.H5([svg_icon('trending_up'), " Pronóstico vs Valores Reales"],
                    className="fw-semibold mb-3 mt-2", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(figure=fig_forecast, config={"displayModeBar": True, "scrollZoom": True})
                ),
                className="shadow-sm border-0 mb-4", style={"border-radius": RADIUS},
            ),
            width=12,
        )),

        # Forecast interpretation
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6([svg_icon('search'), " Lectura del Gráfico de Pronóstico"],
                            className="fw-bold mb-2", style={"color": "#F5C842"}),
                    html.P(
                        "El gráfico muestra tres series: en azul-violeta, la muestra de entrenamiento "
                        "(80% de los datos); en negro, los valores reales del conjunto de prueba (20%); "
                        "y en rojo discontinuo, la predicción del modelo ARIMA con su intervalo de "
                        "confianza del 95% en rosa. Si la línea de predicción se aplana o no captura "
                        "los picos y valles de los valores reales, esto indica las limitaciones "
                        "inherentes del enfoque ARIMA frente a series con alta variabilidad, como las "
                        "tasas financieras colombianas del Banco de la República.",
                        className="small text-secondary mb-0", style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#f8f6ff", "border-radius": RADIUS},
            ),
            width=12,
        )),

        dbc.Row(dbc.Col(_interpretation_card(arima), width=12)),

    ], fluid=True, className="px-3 py-3")
