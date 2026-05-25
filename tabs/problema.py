"""
tabs/problema.py
Pestaña 3 – Descripción del problema / comportamiento de la serie temporal.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tabs.svg_icons import svg_icon
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

from data.generate_data import DF, COLUMN_LABELS, PALETTE


def layout():
    df = DF.copy()

    # ── Serie temporal principal ─────────────────────────────────────────────
    fig_ts = go.Figure()
    fig_ts.add_trace(
        go.Scatter(
            x=df["Fecha"], y=df["TasaColocacionTotal"],
            mode="lines", name="Tasa Total",
            line=dict(color="#D4A017", width=2),
            fill="tozeroy", fillcolor="rgba(212,160,23,0.10)",
        )
    )
    fig_ts.update_layout(
        title="Evolución de la Tasa de Colocación Total (1998–2025)",
        xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified",
        font=dict(family="Jost, sans-serif", size=12, color="#CEC5A8"),
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )
    fig_ts.add_vrect(
        x0="1998-01-01", x1="2002-12-31",
        fillcolor="rgba(255,200,100,0.12)", layer="below", line_width=0,
        annotation_text="Ajuste post-crisis", annotation_position="top left",
    )
    fig_ts.add_vrect(
        x0="2008-01-01", x1="2009-12-31",
        fillcolor="rgba(255,100,100,0.1)", layer="below", line_width=0,
        annotation_text="Crisis financiera global", annotation_position="top left",
    )
    fig_ts.add_vrect(
        x0="2020-01-01", x1="2021-12-31",
        fillcolor="rgba(100,180,255,0.12)", layer="below", line_width=0,
        annotation_text="COVID-19", annotation_position="top left",
    )

    # ── Gráfico multilinea todas las series ───────────────────────────────────
    fig_multi = go.Figure()
    cols = ["CreditosConsumo","CreditosTesoreria","CreditosOrdinarios",
            "CreditosPreferenciales","TasaColocacionBR","TasaColocacionSinTesoreria","TasaColocacionTotal"]
    for col in cols:
        fig_multi.add_trace(
            go.Scatter(
                x=df["Fecha"], y=df[col],
                mode="lines", name=COLUMN_LABELS[col],
                line=dict(color=PALETTE[col], width=1.8),
            )
        )
    fig_multi.update_layout(
        title="Comportamiento Histórico de Todas las Series",
        xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="center", x=0.5, font_size=10),
        hovermode="x unified",
    )

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H3("Descripción del Problema",
                            className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Serie temporal de tasas de interés de colocación – comportamiento, variabilidad y patrones históricos",
                           className="text-muted mb-4"),
                    width=12,
                )
            ),

            # ── Descripción textual ──────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5([svg_icon('clipboard'), " Naturaleza del Dataset"],
                                        className="fw-semibold mb-3", style={"color": "#F5C842"}),
                                html.P(
                                    """
                                    El presente análisis se centra en un conjunto de datos históricos del
                                    Banco de la República, que recoge información mensual desde 1998 sobre
                                    distintos tipos de créditos (consumo, tesorería, ordinarios y preferenciales)
                                    y las tasas de colocación asociadas. La variable Fecha constituye el eje
                                    temporal que organiza las observaciones y permite estudiar la evolución
                                    de estos indicadores financieros a lo largo de más de dos décadas.
                                    """,
                                    className="text-secondary",
                                ),
                                html.P(
                                    """
                                    Este carácter secuencial convierte al dataset en una serie de tiempo,
                                    ideal para explorar tendencias, ciclos y posibles patrones de estacionalidad
                                    en el comportamiento del crédito y las tasas de interés en Colombia.
                                    Dado que los registros son mensuales, la predicción se realizará también
                                    con frecuencia mensual, asegurando coherencia entre la naturaleza de los
                                    datos y el objetivo del modelado.
                                    """,
                                    className="text-secondary",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Gráfico principal ────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(figure=fig_ts, config={"displayModeBar": False})),
                        className="shadow-sm border-0 mb-4",
                        style={"border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Eventos históricos ───────────────────────────────────────────
            dbc.Row(
                [
                    _evento_card(svg_icon('trending_down'), "1998–2002", "Crisis financiera colombiana",
                                 "Las tasas de colocación alcanzaron sus niveles históricos máximos, "
                                 "superando el 50% en algunos segmentos.", "#fff4dc"),
                    _evento_card(svg_icon('globe'), "2008–2009", "Crisis financiera global",
                                 "La crisis de las hipotecas subprime generó volatilidad y presión "
                                 "sobre las tasas locales.", "#fde8e8"),
                    _evento_card(svg_icon('virus'), "2020–2021", "Pandemia COVID-19",
                                 "El Banco de la República implementó política expansiva, "
                                 "llevando las tasas a mínimos históricos.", "#dce8ff"),
                    _evento_card(svg_icon('trending_up'), "2022–2023", "Ciclo de alzas",
                                 "Para controlar la inflación post-pandemia, se inició un agresivo "
                                 "ciclo de incremento de tasas.", "#2E2E38"),
                ],
                className="g-3 mb-4",
            ),

            # ── Gráfico multilinea ───────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(figure=fig_multi, config={"displayModeBar": False})),
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


def _evento_card(icon, periodo, titulo, desc, bg):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(icon, style={
                        "font-size": "2.4rem",
                        "line-height": "1",
                        "margin-bottom": "10px",
                        "filter": "drop-shadow(0 0 8px rgba(212,175,55,0.5))",
                        "display": "block",
                    }),
                    html.P(periodo, className="small fw-bold text-muted mb-1"),
                    html.H6(titulo, className="fw-bold mb-2", style={"color": "#F5C842"}),
                    html.P(desc, className="small text-secondary mb-0"),
                ]
            ),
            className="shadow-sm border-0 h-100",
            style={"background": "#1C1C22", "border-radius": "10px",
                   "border": "1px solid #3D2E0A"},
        ),
        xs=12, sm=6, md=3,
    )
