"""
tabs/rolling.py
Pestaña – Técnica Rolling
Basada en las celdas del notebook EdaVis.ipynb (sección "Tecnica Rolling"):
  - Explicación de supuestos para rolling forecast
  - Búsqueda exhaustiva ARIMA(p,d,q) con d∈{1,2}, p,q∈[0,4]
  - Tabla de p-valores Ljung-Box y Shapiro-Wilk
  - Conclusión sobre la viabilidad del rolling
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tabs.svg_icons import svg_icon
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from model.train_model import load_model_results

# ── Paleta coherente con el proyecto ──────────────────────────────────────
COLOR_GOLD   = "#F5C842"
COLOR_AMBER  = "#D4A017"
COLOR_PASS   = "#27ae60"
COLOR_FAIL   = "#dc3545"
COLOR_WARN   = "#e67e22"
BG_CARD      = "#1C1C22"
BG_DARK      = "#141418"
RADIUS       = "14px"


# ── Figura: heatmap p-valores Ljung-Box por (p, q) para cada d ────────────

def _heatmap_ljungbox(tabla: list, d_val: int) -> go.Figure:
    """Heatmap de p-valores LjungBox para ARIMA(p,d,q) con d fijo."""
    subset = [r for r in tabla if r["d"] == d_val]
    if not subset:
        return go.Figure()

    ps = sorted(set(r["p"] for r in subset))
    qs = sorted(set(r["q"] for r in subset))
    matrix = np.full((len(ps), len(qs)), np.nan)
    for r in subset:
        i = ps.index(r["p"])
        j = qs.index(r["q"])
        matrix[i][j] = r["p_ljungbox"]

    # Texto en celdas
    text = [[f"{matrix[i][j]:.4f}" if not np.isnan(matrix[i][j]) else ""
             for j in range(len(qs))] for i in range(len(ps))]

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=[f"q={q}" for q in qs],
        y=[f"p={p}" for p in ps],
        text=text,
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        colorscale=[
            [0.0,  "#8B0000"],   # rojo oscuro → p muy bajo
            [0.05, "#cc3300"],
            [0.10, "#e67e22"],
            [0.5,  "#f5c842"],
            [1.0,  "#27ae60"],   # verde → p alto (independencia)
        ],
        zmin=0, zmax=0.5,
        colorbar=dict(
            title=dict(text="p-valor LB", font=dict(color="#CEC5A8", size=11)),
            tickfont=dict(color="#CEC5A8", size=10),
            thickness=12,
        ),
        hovertemplate="ARIMA(%{y},%d,%{x})<br>p LjungBox: %{z:.6f}<extra></extra>".replace("%d", str(d_val)),
    ))
    fig.add_shape(type="line", x0=-0.5, x1=len(qs)-0.5, y0=-0.5, y1=len(ps)-0.5,
                  line=dict(color="rgba(0,0,0,0)", width=0))

    fig.update_layout(
        title=dict(
            text=f"p-valores Ljung-Box — ARIMA(p,{d_val},q)",
            font=dict(color=COLOR_GOLD, size=13),
        ),
        xaxis=dict(tickfont=dict(color="#CEC5A8", size=11), gridcolor="#2A2A30"),
        yaxis=dict(tickfont=dict(color="#CEC5A8", size=11), gridcolor="#2A2A30"),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=60, r=30, t=55, b=50),
        height=340,
        annotations=[dict(
            text="Línea 0.05 → zona verde = independencia cumplida",
            xref="paper", yref="paper", x=0, y=-0.15,
            showarrow=False,
            font=dict(color="#7a6f5a", size=10),
        )],
    )
    return fig




# ── Tarjeta de supuesto rolling ──────────────────────────────────────────

def _supuesto_rolling_card(numero, titulo, como, color_borde):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H6(
                    [svg_icon(f"n{numero}"), f"  {numero}. {titulo}"],
                    className="fw-bold mb-2", style={"color": COLOR_GOLD},
                ),
                html.P(como, className="small text-secondary mb-0",
                       style={"text-align": "justify"}),
            ]),
            className="shadow-sm border-0 h-100",
            style={"background": BG_CARD, "border-radius": RADIUS,
                   "border-top": f"4px solid {color_borde}"},
        ),
        xs=12, sm=6, md=4, className="mb-3",
    )


# ── Layout ────────────────────────────────────────────────────────────────

def layout():
    res     = load_model_results()
    rolling = res.get("rolling", {})
    tabla   = rolling.get("tabla", [])
    alguna  = rolling.get("alguna_independencia", False)
    concl   = rolling.get("conclusion", "Datos no disponibles. Regenere el modelo.")
    total   = rolling.get("total_combinaciones", len(tabla))

    # Contar cuántas pasan cada supuesto
    n_lb_ok = sum(1 for r in tabla if r.get("independencia", False))
    n_sw_ok = sum(1 for r in tabla if r.get("normalidad", False))

    # Preparar tabla para dash_table
    tabla_df_rows = [
        {
            "ARIMA": f"({r['p']},{r['d']},{r['q']})",
            "p": r["p"], "d": r["d"], "q": r["q"],
            "p-valor LjungBox": f"{r['p_ljungbox']:.6f}",
            "p-valor Shapiro": f"{r['p_shapiro']:.6f}",
            "Independencia": "✓" if r.get("independencia") else "✗",
            "Normalidad":    "✓" if r.get("normalidad")    else "✗",
        }
        for r in tabla
    ]

    fig_hm1 = _heatmap_ljungbox(tabla, d_val=1)
    fig_hm2 = _heatmap_ljungbox(tabla, d_val=2)

    return dbc.Container([

        # ── Encabezado ────────────────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H3("Técnica Rolling — Viabilidad y Supuestos",
                    className="fw-bold pt-3 mb-1", style={"color": COLOR_GOLD}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            html.P(
                "Evaluación de los supuestos estadísticos requeridos para aplicar pronósticos "
                "continuos (rolling forecast) en la serie TasaColocacionTotal.",
                className="text-muted mb-4",
            ),
            width=12,
        )),

        # ── ¿Qué es la técnica rolling? ──────────────────────────────
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5([svg_icon('info'), " ¿Qué es la Técnica Rolling?"],
                            className="fw-semibold mb-3", style={"color": COLOR_GOLD}),
                    html.P(
                        "La técnica rolling (o ventana deslizante) consiste en ajustar el modelo "
                        "de predicción de forma continua: en cada paso de tiempo se reajusta el "
                        "modelo usando una ventana fija de observaciones pasadas (rolling window) "
                        "y se genera el pronóstico para el siguiente punto. Esta estrategia permite "
                        "capturar cambios estructurales en la serie y actualizar los parámetros del "
                        "modelo dinámicamente.",
                        className="text-secondary mb-2",
                        style={"text-align": "justify"},
                    ),
                    html.P(
                        "Para que el rolling forecast sea estadísticamente riguroso, se deben "
                        "verificar cinco supuestos clave antes de su aplicación. Si alguno de ellos "
                        "se viola, las predicciones carecen de fundamento estadístico y pueden "
                        "inducir a conclusiones erróneas.",
                        className="text-secondary mb-0",
                        style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": BG_CARD, "border-radius": RADIUS},
            ),
            width=12,
        )),

        # ── Cinco supuestos ──────────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('clipboard'), " Supuestos para Aplicar la Técnica Rolling"],
                    className="fw-semibold mb-3", style={"color": COLOR_GOLD}),
            width=12,
        )),
        dbc.Row([
            _supuesto_rolling_card(
                1, "Estacionariedad",
                "Es el supuesto más importante. La media, varianza y autocorrelación de la serie "
                "no deben cambiar con el tiempo. Se verifica con la prueba ADF: si p > 0.05 la "
                "serie no es estacionaria y debe transformarse (diferenciación) antes de aplicar "
                "el modelo en ventana móvil.",
                "#27ae60",
            ),
            _supuesto_rolling_card(
                2, "Independencia y Ausencia de Autocorrelación",
                "Para que el rolling forecast sea efectivo, la serie no debe ser ruido blanco ni "
                "caminata aleatoria. Se analizan los gráficos ACF y PACF para identificar patrones "
                "predecibles. La prueba de Ljung-Box determina si la autocorrelación es "
                "estadísticamente significativa.",
                COLOR_AMBER,
            ),
            _supuesto_rolling_card(
                3, "Varianza Constante (Homocedasticidad)",
                "La magnitud de las fluctuaciones debe ser estable. Si la varianza cambia con el "
                "tiempo (heterocedasticidad), el estadístico móvil o el pronóstico puede verse "
                "distorsionado. Se recomienda aplicar transformaciones logarítmicas o de potencia "
                "para estabilizarla en series financieras volátiles.",
                COLOR_WARN,
            ),
            _supuesto_rolling_card(
                4, "Normalidad de los Residuos",
                "Los errores del modelo deben seguir una distribución normal con media cero. "
                "Se aplican pruebas como Shapiro-Wilk o Kolmogorov-Smirnov para cuantificar la "
                "probabilidad de que los datos procedan de una distribución gaussiana.",
                "#e74c3c",
            ),
            _supuesto_rolling_card(
                5, "Tamaño de Ventana y Datos Suficientes",
                "Para una estimación fiable de la autocorrelación en cada paso del rolling, se "
                "recomienda al menos 50 observaciones por ventana. Se debe definir adecuadamente "
                "el tamaño de ventana (k) y el paso (l), ya que determinan cuánta información "
                "histórica se considera en cada cálculo.",
                "#7b6cf7",
            ),
        ], className="g-3 mb-4"),

        # ── Resumen de la búsqueda ────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('bar_chart'), " Búsqueda Exhaustiva de Parámetros ARIMA"],
                    className="fw-semibold mb-3", style={"color": COLOR_GOLD}),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.P("Combinaciones evaluadas", className="small text-muted mb-0"),
                        html.H2(str(total), className="fw-bold mb-0",
                                style={"color": COLOR_GOLD}),
                        html.P("d ∈ {1, 2} · p, q ∈ [0, 4]",
                               className="small text-secondary mt-1 mb-0"),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={"background": BG_CARD, "border-radius": RADIUS,
                           "border-top": f"4px solid {COLOR_AMBER}"},
                ),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.P("Pasan independencia (LB p ≥ 0.05)", className="small text-muted mb-0"),
                        html.H2(str(n_lb_ok), className="fw-bold mb-0",
                                style={"color": COLOR_PASS if n_lb_ok > 0 else COLOR_FAIL}),
                        html.P(f"de {total} combinaciones",
                               className="small text-secondary mt-1 mb-0"),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={"background": BG_CARD, "border-radius": RADIUS,
                           "border-top": f"4px solid {COLOR_PASS if n_lb_ok > 0 else COLOR_FAIL}"},
                ),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.P("Pasan normalidad (SW p ≥ 0.05)", className="small text-muted mb-0"),
                        html.H2(str(n_sw_ok), className="fw-bold mb-0",
                                style={"color": COLOR_PASS if n_sw_ok > 0 else COLOR_FAIL}),
                        html.P(f"de {total} combinaciones",
                               className="small text-secondary mt-1 mb-0"),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={"background": BG_CARD, "border-radius": RADIUS,
                           "border-top": f"4px solid {COLOR_PASS if n_sw_ok > 0 else COLOR_FAIL}"},
                ),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.P("Veredicto Rolling", className="small text-muted mb-0"),
                        html.H4(
                            "Viable" if alguna else "No viable",
                            className="fw-bold mb-0 mt-1",
                            style={"color": COLOR_PASS if alguna else COLOR_FAIL},
                        ),
                        html.P(
                            "al menos 1 combinación ok" if alguna else "ninguna combinación cumple",
                            className="small text-secondary mt-1 mb-0",
                        ),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={"background": BG_CARD, "border-radius": RADIUS,
                           "border-top": f"4px solid {COLOR_PASS if alguna else COLOR_FAIL}"},
                ),
                xs=6, md=3, className="mb-3",
            ),
        ], className="mb-4"),

        # ── Heatmaps p-valores ───────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('search'), " Mapas de Calor — p-valores Ljung-Box"],
                    className="fw-semibold mb-3", style={"color": COLOR_GOLD}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    html.P(
                        "Los mapas de calor muestran el p-valor de la prueba Ljung-Box para cada "
                        "combinación (p, q) con d fijo. Las celdas en rojo indican autocorrelación "
                        "residual significativa (p < 0.05 → supuesto de independencia violado). "
                        "Solo las celdas verdes (p ≥ 0.05) permitirían aplicar rolling de forma rigurosa.",
                        className="small text-secondary mb-0",
                        style={"text-align": "justify"},
                    )
                ),
                className="shadow-sm border-0 mb-3",
                style={"background": BG_CARD, "border-radius": RADIUS},
            ),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_hm1, config={"displayModeBar": False})),
                    className="shadow-sm border-0",
                    style={"border-radius": RADIUS},
                ),
                md=6, className="mb-4",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_hm2, config={"displayModeBar": False})),
                    className="shadow-sm border-0",
                    style={"border-radius": RADIUS},
                ),
                md=6, className="mb-4",
            ),
        ]),

        # ── Tabla de resultados ──────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('clipboard'), " Tabla de Resultados — Todas las Combinaciones"],
                    className="fw-semibold mb-3", style={"color": COLOR_GOLD}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dash_table.DataTable(
                        data=tabla_df_rows,
                        columns=[
                            {"name": "ARIMA(p,d,q)", "id": "ARIMA"},
                            {"name": "p", "id": "p"},
                            {"name": "d", "id": "d"},
                            {"name": "q", "id": "q"},
                            {"name": "p-valor Ljung-Box", "id": "p-valor LjungBox"},
                            {"name": "p-valor Shapiro-Wilk", "id": "p-valor Shapiro"},
                            {"name": "Independencia", "id": "Independencia"},
                            {"name": "Normalidad", "id": "Normalidad"},
                        ],
                        sort_action="native",
                        filter_action="native",
                        page_size=15,
                        style_table={"overflowX": "auto"},
                        style_header={
                            "backgroundColor": "#0A0A0C",
                            "color": COLOR_GOLD,
                            "fontWeight": "bold",
                            "fontSize": "12px",
                            "border": "1px solid #2A2A30",
                            "textAlign": "center",
                        },
                        style_cell={
                            "backgroundColor": BG_CARD,
                            "color": "#CEC5A8",
                            "fontSize": "12px",
                            "border": "1px solid #2A2A30",
                            "textAlign": "center",
                            "padding": "6px 10px",
                        },
                        style_data_conditional=[
                            {
                                "if": {"filter_query": "{Independencia} = ✓",
                                       "column_id": "Independencia"},
                                "color": COLOR_PASS,
                                "fontWeight": "bold",
                            },
                            {
                                "if": {"filter_query": "{Independencia} = ✗",
                                       "column_id": "Independencia"},
                                "color": COLOR_FAIL,
                            },
                            {
                                "if": {"filter_query": "{Normalidad} = ✓",
                                       "column_id": "Normalidad"},
                                "color": COLOR_PASS,
                                "fontWeight": "bold",
                            },
                            {
                                "if": {"filter_query": "{Normalidad} = ✗",
                                       "column_id": "Normalidad"},
                                "color": COLOR_FAIL,
                            },
                            {"if": {"row_index": "odd"},
                             "backgroundColor": "#18181e"},
                        ],
                    ),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": BG_CARD, "border-radius": RADIUS},
            ),
            width=12,
        )),

        # ── Conclusión ────────────────────────────────────────────────
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5([svg_icon('pin'), " Conclusión sobre la Viabilidad del Rolling"],
                            className="fw-semibold mb-2", style={"color": COLOR_GOLD}),
                    html.P(concl, className="text-secondary mb-3",
                           style={"text-align": "justify"}),
                    html.Hr(className="my-2"),
                    html.P(
                        "La autocorrelación residual persistente en todos los modelos evaluados "
                        "confirma que la serie TasaColocacionTotal presenta una estructura de "
                        "dependencia temporal que ninguna combinación ARIMA clásica logra "
                        "capturar completamente. Desde la perspectiva de la complejidad "
                        "computacional y estadística, esto implica que el uso de la técnica "
                        "rolling sobre modelos ARIMA no garantiza la rigurosidad estadística "
                        "necesaria para validar los pronósticos. Se recomienda explorar modelos "
                        "no lineales (LSTM, SVR) o modelos con heteroscedasticidad condicional "
                        "(GARCH) que puedan capturar la dinámica compleja de la serie.",
                        className="small text-secondary mb-0",
                        style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0",
                style={
                    "background": "#fff3cd" if not alguna else "#d4edda",
                    "border-radius": RADIUS,
                    "border-left": f"5px solid {COLOR_WARN if not alguna else COLOR_PASS}",
                },
            ),
            width=12,
        )),

    ], fluid=True, className="px-3 py-3")
