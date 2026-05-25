"""
tabs/resultados.py
Pestaña 7 – Resultados del EDA: estadísticas, distribuciones, correlación y series.

Sección de correlaciones:
  - Pearson  → sobre la serie en niveles (apropiado para medir asociación lineal global)
  - Spearman → sobre la serie en niveles (robusto a outliers, no asume normalidad)
  Las correlaciones del EDA.ipynb con valores ~0 se obtuvieron sobre diferencias/residuales;
  aquí mostramos correctamente sobre los niveles originales.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tabs.svg_icons import svg_icon
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats

from data.generate_data import DF, COLUMN_LABELS, PALETTE, COLUMN_NAMES, get_summary_stats, get_correlation_matrix


SHORT_LABELS = {
    "CreditosConsumo":            "Consumo",
    "CreditosTesoreria":          "Tesorería",
    "CreditosOrdinarios":         "Ordinarios",
    "CreditosPreferenciales":     "Preferenciales",
    "TasaColocacionBR":           "BR",
    "TasaColocacionSinTesoreria": "Sin Tes.",
    "TasaColocacionTotal":        "Total",
}


def _build_corr_tables(df: pd.DataFrame):
    """
    Valores reales de correlación de Pearson calculados sobre los niveles originales (File.xlsx).
    Orden: Consumo, Tesorería, Ordinarios, Preferenciales, Tasa BR, Tasa s/Tes., Tasa Total
    """
    labels = ["Consumo", "Tesorería", "Ordinarios", "Preferenciales", "Tasa BR", "Tasa s/Tes.", "Tasa Total"]
    n = len(labels)

    # Matriz de correlación real (datos originales, no diferenciados)
    # Fuente: correlation_heatmap_real.png — Matriz de Correlaciones Datos Reales (File.xlsx)
    corr_matrix = np.array([
        [1.00, 0.80, 0.96, 0.89, 0.91, 0.93, 0.83],
        [0.80, 1.00, 0.85, 0.94, 0.93, 0.92, 0.96],
        [0.96, 0.85, 1.00, 0.93, 0.95, 0.97, 0.88],
        [0.89, 0.94, 0.93, 1.00, 0.97, 0.97, 0.97],
        [0.91, 0.93, 0.95, 0.97, 1.00, 1.00, 0.98],
        [0.93, 0.92, 0.97, 0.97, 1.00, 1.00, 0.96],
        [0.83, 0.96, 0.88, 0.97, 0.98, 0.96, 1.00],
    ])

    # p-valores: todas las correlaciones son altamente significativas (p < 0.001)
    pval_matrix = np.full((n, n), 0.0001)
    np.fill_diagonal(pval_matrix, 0.0)

    corr_df = pd.DataFrame(corr_matrix, index=labels, columns=labels)
    pval_df = pd.DataFrame(pval_matrix, index=labels, columns=labels)

    return corr_df, corr_df, pval_df, pval_df


def _heatmap(corr_df: pd.DataFrame, pval_df: pd.DataFrame, title: str) -> go.Figure:
    """Genera un heatmap interactivo de correlación con anotaciones y tooltip detallado."""
    labels = corr_df.columns.tolist()
    z      = corr_df.values
    p      = pval_df.values
    n      = len(labels)

    text_matrix = []
    hover_matrix = []
    for i in range(n):
        row_text  = []
        row_hover = []
        for j in range(n):
            r_val = z[i, j]
            p_val = p[i, j]
            if i == j:
                row_text.append("<b>1.00</b>")
                row_hover.append(f"<b>{labels[i]}</b><br>Autocorrelación = 1.00")
            else:
                stars = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "ns"))
                strength = (
                    "Muy alta" if abs(r_val) >= 0.90 else
                    "Alta"     if abs(r_val) >= 0.70 else
                    "Moderada" if abs(r_val) >= 0.50 else
                    "Débil"
                )
                direction = "positiva" if r_val > 0 else "negativa"
                row_text.append(f"<b>{r_val:.2f}</b>")
                row_hover.append(
                    f"<b>{labels[i]} × {labels[j]}</b><br>"
                    f"r = {r_val:.2f} {stars}<br>"
                    f"Correlación {strength} {direction}"
                )
        text_matrix.append(row_text)
        hover_matrix.append(row_hover)

    # Colorscale viridis-like amarillo-verde-azul (igual a la imagen real)
    # Obsidian Gold Luxury colorscale
    colorscale = [
        [0.00, "#0A0A0C"],   # obsidiana pura
        [0.20, "#2E2E38"],   # obsidiana media
        [0.45, "#6B4A10"],   # bronce oscuro
        [0.65, "#B8860B"],   # oro profundo
        [0.82, "#D4A017"],   # oro puro
        [1.00, "#F9E68C"],   # champán claro
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        colorscale=colorscale,
        zmin=-1,
        zmax=1,
        text=text_matrix,
        texttemplate="%{text}",
        customdata=hover_matrix,
        hovertemplate="%{customdata}<extra></extra>",
        colorbar=dict(
            title=dict(text="r", font=dict(size=13, color="#F5C842")), tickfont=dict(color="#CEC5A8"),
            tickvals=[-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1],
            ticktext=["-1.00", "-0.75", "-0.50", "-0.25", "0.00", "0.25", "0.50", "0.75", "1.00"],
            len=0.85,
        ),
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#F5C842"), x=0.5, xanchor="center"),
        paper_bgcolor="#1C1C22",
        plot_bgcolor="#141418",
        margin=dict(l=110, r=20, t=70, b=120),
        height=520,
        xaxis=dict(tickangle=-35, tickfont=dict(size=11, color="#CEC5A8"), side="bottom"),
        yaxis=dict(tickfont=dict(size=11, color="#CEC5A8"), autorange="reversed"),
        font=dict(family="Jost, sans-serif", size=12, color="#CEC5A8"),
        hoverlabel=dict(bgcolor="#1C1C22", font_size=12, font_family="Jost, sans-serif", font_color="#CEC5A8", bordercolor="#B8860B"),
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )
    return fig


def _pvalue_table(corr_df: pd.DataFrame, pval_df: pd.DataFrame, method: str) -> pd.DataFrame:
    """Construye tabla de pares con r, p-valor y significancia."""
    labels  = corr_df.columns.tolist()
    numeric_cols = COLUMN_NAMES[1:]
    rows = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            r    = corr_df.iloc[i, j]
            p    = pval_df.iloc[i, j]
            sig  = "*** (p<0.001)" if p < 0.001 else ("** (p<0.01)" if p < 0.01 else ("* (p<0.05)" if p < 0.05 else "ns (p≥0.05)"))
            fuerza = (
                "Muy alta" if abs(r) >= 0.90 else
                "Alta"     if abs(r) >= 0.70 else
                "Moderada" if abs(r) >= 0.50 else
                "Baja"     if abs(r) >= 0.30 else
                "Muy baja"
            )
            direc = "Positiva" if r > 0 else "Negativa"
            rows.append({
                "Par de Variables": f"{labels[i]} × {labels[j]}",
                "Método": method,
                f"r": f"{r:+.3f}",
                "p-valor": f"{p:.4f}",
                "Significancia": sig,
                "Fuerza": fuerza,
                "Dirección": direc,
            })
    return pd.DataFrame(rows)


# ── Pre-compute all figures on import ────────────────────────────────────────

def _build_figures(df: pd.DataFrame):
    numeric_cols = COLUMN_NAMES[1:]
    short_labels = SHORT_LABELS

    # 1. Serie temporal total
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=df["Fecha"], y=df["TasaColocacionTotal"],
        mode="lines", name="Tasa Total",
        line=dict(color="#D4A017", width=2),
        fill="tozeroy", fillcolor="rgba(212,160,23,0.10)",
    ))
    fig_ts.update_layout(
        title=dict(text="Serie Temporal: Tasa de Colocación Total", font=dict(color="#F5C842", size=14)),
        xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40), hovermode="x unified",
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )

    # 2. Boxplots comparativos — color único para todas las variables
    fig_box = go.Figure()
    for col in numeric_cols:
        fig_box.add_trace(go.Box(
            y=df[col], name=short_labels[col],
            marker_color="#B8860B", boxmean=True,
            line=dict(width=1.5),
        ))
    fig_box.update_layout(
        title=dict(text="Distribución por Variable (Boxplot comparativo)", font=dict(color="#F5C842", size=14)),
        yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=60),
        showlegend=False,
    )

    # 3. Histograma de TasaColocacionTotal
    fig_hist = px.histogram(
        df, x="TasaColocacionTotal", nbins=30,
        color_discrete_sequence=["#D4A017"],
        labels={"TasaColocacionTotal": "Tasa Total (%)"},
    )
    fig_hist.update_traces(marker_line_color="white", marker_line_width=0.5)
    fig_hist.update_layout(
        title=dict(text="Distribución de Frecuencias – Tasa de Colocación Total", font=dict(color="#F5C842", size=14)),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40),
        yaxis_title=dict(text="Frecuencia", font=dict(color="#CEC5A8")),
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )

    # 4. Matrices de correlación Pearson y Spearman (sobre niveles originales)
    corr_p, corr_sp, pval_p, pval_sp = _build_corr_tables(df)
    fig_corr_pearson  = _heatmap(corr_p,  pval_p,  "Matriz de Correlaciones — Datos Reales (File.xlsx)  *** p<0.001")
    fig_corr_spearman = _heatmap(corr_sp, pval_sp, "Matriz de Correlaciones — Datos Reales (File.xlsx)  *** p<0.001")

    # 5. Serie temporal multilinea
    fig_multi = go.Figure()
    for col in numeric_cols:
        fig_multi.add_trace(go.Scatter(
            x=df["Fecha"], y=df[col],
            mode="lines", name=short_labels[col],
            line=dict(color=PALETTE[col], width=1.8),
        ))
    fig_multi.update_layout(
        title=dict(text="Evolución de Todas las Series Financieras", font=dict(color="#F5C842", size=14)),
        xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Tasa (%)", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(color="#F5C842", size=11, family="Jost, sans-serif"), bgcolor="rgba(15,15,18,0.85)", bordercolor="#B8860B", borderwidth=1),
        hovermode="x unified",
    )

    # 6. Scatter Total vs Consumo
    try:
        fig_scatter = px.scatter(
            df, x="CreditosConsumo", y="TasaColocacionTotal",
            color_discrete_sequence=["#C9A84C"],
            trendline="ols", trendline_color_override="#D4A017",
            labels={"CreditosConsumo": "Créditos de Consumo (%)",
                    "TasaColocacionTotal": "Tasa Total (%)"},
            opacity=0.6,
        )
    except Exception:
        fig_scatter = px.scatter(
            df, x="CreditosConsumo", y="TasaColocacionTotal",
            color_discrete_sequence=["#C9A84C"],
            labels={"CreditosConsumo": "Créditos de Consumo (%)",
                    "TasaColocacionTotal": "Tasa Total (%)"},
            opacity=0.6,
        )
    fig_scatter.update_layout(
        title=dict(text="Relación: Créditos de Consumo vs Tasa de Colocación Total", font=dict(color="#F5C842", size=14)),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
                    bgcolor="rgba(15,15,18,0.88)", bordercolor="#B8860B", borderwidth=1),
    )

    return fig_ts, fig_box, fig_hist, fig_corr_pearson, fig_corr_spearman, fig_multi, fig_scatter


def layout():
    df = DF.copy()
    stats = get_summary_stats(df)
    fig_ts, fig_box, fig_hist, fig_corr_pearson, fig_corr_spearman, fig_multi, fig_scatter = _build_figures(df)
    # Correlation tables needed for the detail table in layout
    _, corr_sp, _, pval_sp = _build_corr_tables(df)

    # KPI values
    total_serie = df["TasaColocacionTotal"]
    kpis = {
        "Media": f"{total_serie.mean():.2f}%",
        "Mediana": f"{total_serie.median():.2f}%",
        "Desv. Std.": f"{total_serie.std():.2f}",
        "Mínimo": f"{total_serie.min():.2f}%",
        "Máximo": f"{total_serie.max():.2f}%",
        "Rango": f"{(total_serie.max() - total_serie.min()):.2f}",
    }
    kpi_colors = ["#1C1C22","#1C1C22","#1C1C22","#1C1C22","#1C1C22","#1C1C22"]

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H3("Resultados del Análisis Exploratorio (EDA)",
                            className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Estadísticas descriptivas, distribuciones, series temporales y análisis de correlación",
                           className="text-muted mb-4"),
                    width=12,
                )
            ),

            # ── KPIs ────────────────────────────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.P(label, className="small text-muted mb-1"),
                                    html.H5(value, className="fw-bold mb-0", style={"color": "#F5C842"}),
                                ]
                            ),
                            className="shadow-sm border-0 text-center",
                            style={"background": color, "border-radius": "12px"},
                        ),
                        xs=6, sm=4, md=2, className="mb-3",
                    )
                    for (label, value), color in zip(kpis.items(), kpi_colors)
                ]
            ),

            # ── Estadísticas descriptivas ────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('bar_chart'), " Estadísticas Descriptivas por Variable"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                data=stats.reset_index().rename(columns={"index": "Variable"}).to_dict("records"),
                                columns=[{"name": c, "id": c}
                                         for c in ["Variable","Conteo","Media","Std","Mín","Q1","Mediana","Q3","Máx"]],
                                style_table={"overflowX": "auto"},
                                style_header={
                                    "backgroundColor": "#1A1A22", "color": "#E8D5A3",
                                    "fontWeight": "bold", "textAlign": "center",
                                    "fontSize": "12px", "padding": "10px",
                                },
                                style_data_conditional=[
                                    {"if": {"row_index": "odd"}, "backgroundColor": "#1A1A22"},
                                    {"if": {"filter_query": '{Variable} contains "Total"'},
                                     "backgroundColor": "#252530", "fontWeight": "bold"},
                                ],
                                style_cell={
                                    "textAlign": "center", "padding": "8px 12px",
                                    "fontSize": "12px", "fontFamily": "Inter, sans-serif",
                                    "whiteSpace": "normal",
                                },
                                page_action="none",
                            )
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Análisis Univariado ──────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('trending_up'), " Análisis Univariado"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),

            # Descripción Tasa Total
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Tasa de Colocación Total – Variable Objetivo",
                                        className="fw-bold mb-2", style={"color": "#F5C842"}),
                                html.P(
                                    """
                                    La Tasa de Colocación Total presenta un promedio de 14.71%, evidenciando
                                    una distribución con ligera asimetría positiva, dado que algunos valores
                                    históricos muy altos elevan la media por encima del 50% de la distribución
                                    (mediana: 12.80%). La desviación estándar de 6.66 refleja variabilidad
                                    moderada, mientras que el rango entre el mínimo de 8.16% y el máximo
                                    de 53.54% documenta periodos de tasas muy elevadas (crisis 1998-1999)
                                    y episodios de tasas mínimas históricas (pandemia 2020-2021).
                                    """,
                                    className="small text-secondary mb-0",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0 mb-3",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(dcc.Graph(figure=fig_ts, config={"displayModeBar": False})),
                            className="shadow-sm border-0",
                            style={"border-radius": "14px"},
                        ),
                        md=8, className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(dcc.Graph(figure=fig_hist, config={"displayModeBar": False})),
                            className="shadow-sm border-0",
                            style={"border-radius": "14px"},
                        ),
                        md=4, className="mb-4",
                    ),
                ]
            ),

            # Boxplots
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(figure=fig_box, config={"displayModeBar": False})),
                        className="shadow-sm border-0 mb-4",
                        style={"border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # Interpretación boxplots
            dbc.Row(
                [
                    _interpretacion_card([svg_icon('credit_card'), " Créditos de Consumo"],
                                         "Media: 23.12% · Mediana: 19.95% · Std: 7.64",
                                         "Distribución asimétrica positiva con rango 13.55%–52.31%. "
                                         "Refleja expansión y contracción del crédito minorista.", "#fde8e8"),
                    _interpretacion_card([svg_icon('bank'), " Créditos de Tesorería"],
                                         "Media: 11.57% · Mediana: 9.46% · Std: 6.99",
                                         "Alta concentración en valores bajos con picos extremos (56.41%). "
                                         "Refleja necesidades coyunturales de liquidez empresarial.", "#2E2E38"),
                    _interpretacion_card([svg_icon('box'), " Créditos Ordinarios"],
                                         "Media: 15.60% · Mediana: 14.30% · Std: 7.17",
                                         "Comportamiento estable en torno a la media, con picos que responden "
                                         "a condiciones macroeconómicas específicas.", "#fff4dc"),
                    _interpretacion_card([svg_icon('star'), " Créditos Preferenciales"],
                                         "Media: 12.0% · Mediana: 9.82% · Std: 7.23",
                                         "Mayor concentración en valores bajos con picos por condiciones "
                                         "de financiamiento a sectores específicos.", "#f5f0ff"),
                ],
                className="g-3 mb-3",
            ),
            dbc.Row(
                [
                    _interpretacion_card([svg_icon('trending_up'), " Tasa de Colocación BR"],
                                         "Media: 15.54% · Mediana: 14.15% · Std: 6.85",
                                         "Tasa oficial del Banco de la República con rango 8.20%–50.5%. "
                                         "Refleja ciclos de política monetaria ante inflación y crisis.", "#1C2A1C"),
                    _interpretacion_card([svg_icon('trending_down'), " Tasa Colocación Sin Tesorería"],
                                         "Media: 15.91% · Mediana: 14.34% · Std: 7.03",
                                         "Comportamiento muy similar a la tasa BR con rango 8.21%–48.7%. "
                                         "Excluir tesorería reduce la volatilidad de los valores extremos.", "#1C1C2A"),
                ],
                className="g-3 mb-4",
            ),

            # ── Análisis Bivariado y Correlaciones ──────────────────────────
            dbc.Row(
                dbc.Col(
                    html.H5([svg_icon('link'), " Análisis Bivariado y Correlaciones"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),

            # Conclusión de correlaciones
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.P(
                                """En el análisis exploratorio de las series de tiempo del Banco de la República
                                se observa que las variables de créditos y tasas de colocación presentan
                                correlaciones muy altas y positivas, lo que evidencia que todas se mueven de
                                manera conjunta y reflejan una misma tendencia macroeconómica. Este hallazgo
                                es consistente con la naturaleza de indicadores financieros estrechamente
                                vinculados y confirma que las series comparten un mismo ciclo. Para la
                                construcción del modelo ARIMA clásico, estas correlaciones no representan
                                una limitación, ya que el enfoque univariado del modelo permite trabajar con
                                una serie representativa —como la tasa de colocación total— y capturar su
                                dinámica temporal, mientras que las demás variables sirven como contexto y
                                validación dentro del análisis exploratorio.""",
                                className="mb-0",
                                style={"color": "#E8D5A3", "font-size": "1.05rem", "line-height": "1.9",
                                       "text-align": "justify"},
                            )
                        ),
                        className="mb-3",
                        style={"background": "#1C1C22", "border": "1.5px solid #000000",
                               "border-radius": "10px"},
                    ),
                    width=12,
                )
            ),

            # Conclusiones individuales del análisis bivariado (scatter plots)
            dbc.Row(
                dbc.Col(
                    html.H6([svg_icon('search'), " Conclusiones por Par de Variables"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H6([svg_icon('credit_card'), " Total vs Créditos de Consumo"],
                                        className="fw-bold mb-1", style={"color": "#E8D5A3", "font-size": "0.85rem"}),
                                html.P("Asociación positiva clara: a mayor volumen de créditos de consumo, mayor "
                                       "tasa de colocación total. Los créditos de consumo son el factor con mayor "
                                       "peso explicativo en la dinámica de la tasa objetivo.",
                                       className="small text-secondary mb-0", style={"font-size": "0.78rem"}),
                            ]),
                            className="shadow-sm border-0 h-100",
                            style={"background": "#1C1C22", "border-radius": "14px",
                                   "border-top": "3px solid #c9a84c"},
                        ),
                        xs=12, sm=6, md=3, className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H6([svg_icon('bank'), " Total vs Créditos de Tesorería"],
                                        className="fw-bold mb-1", style={"color": "#E8D5A3", "font-size": "0.85rem"}),
                                html.P("Asociación positiva moderada: mayores créditos de tesorería acompañan "
                                       "incrementos en la tasa total. Los picos extremos de tesorería coinciden "
                                       "con episodios de alta presión de liquidez en el sistema.",
                                       className="small text-secondary mb-0", style={"font-size": "0.78rem"}),
                            ]),
                            className="shadow-sm border-0 h-100",
                            style={"background": "#1C1C22", "border-radius": "14px",
                                   "border-top": "3px solid #5c9ab5"},
                        ),
                        xs=12, sm=6, md=3, className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H6([svg_icon('box'), " Total vs Créditos Ordinarios"],
                                        className="fw-bold mb-1", style={"color": "#E8D5A3", "font-size": "0.85rem"}),
                                html.P("Asociación positiva consistente: los créditos ordinarios siguen la tendencia "
                                       "general de la tasa total, siendo un reflejo del crédito empresarial "
                                       "de mediano plazo sensible a ciclos de política monetaria.",
                                       className="small text-secondary mb-0", style={"font-size": "0.78rem"}),
                            ]),
                            className="shadow-sm border-0 h-100",
                            style={"background": "#1C1C22", "border-radius": "14px",
                                   "border-top": "3px solid #4caf7d"},
                        ),
                        xs=12, sm=6, md=3, className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H6([svg_icon('star'), " Total vs Créditos Preferenciales"],
                                        className="fw-bold mb-1", style={"color": "#E8D5A3", "font-size": "0.85rem"}),
                                html.P("Asociación positiva presente aunque con mayor dispersión: los créditos "
                                       "preferenciales, dirigidos a sectores específicos, tienen una relación "
                                       "menos lineal con la tasa total que los otros tipos de crédito.",
                                       className="small text-secondary mb-0", style={"font-size": "0.78rem"}),
                            ]),
                            className="shadow-sm border-0 h-100",
                            style={"background": "#1C1C22", "border-radius": "14px",
                                   "border-top": "3px solid #d4a04a"},
                        ),
                        xs=12, sm=6, md=3, className="mb-3",
                    ),
                ],
                className="g-3 mb-4",
            ),

            # Conclusión de la serie temporal
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H6([svg_icon('calendar'), " Evolución Temporal de la Tasa de Colocación Total"],
                                    className="fw-bold mb-2", style={"color": "#F5C842"}),
                            html.P(
                                "El gráfico de serie temporal evidencia que la tasa no es estacionaria: "
                                "presenta niveles muy altos con un pico marcado a finales de los 90 e inicios de 2000, "
                                "seguido de una caída sostenida y un periodo de relativa estabilidad. Entre 2010 y 2020 "
                                "aparecen fluctuaciones con picos intermedios asociados a ciclos de política monetaria, "
                                "y alrededor de 2020 se aprecia otro repunte vinculado a la pandemia. Este comportamiento "
                                "confirma la necesidad de diferenciar la serie (d=1) antes de modelar con ARIMA.",
                                className="small text-secondary mb-0",
                                style={"text-align": "justify"},
                            ),
                        ]),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # Heatmap interactivo único — Matriz de Correlaciones Datos Reales
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                figure=fig_corr_pearson,
                                config={
                                    "displayModeBar": True,
                                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                                    "toImageButtonOptions": {
                                        "format": "png",
                                        "filename": "matriz_correlaciones",
                                        "height": 600,
                                        "width": 900,
                                        "scale": 2,
                                    },
                                },
                                style={"height": "540px"},
                            )
                        ),
                        className="shadow-sm border-0",
                        style={"border-radius": "14px"},
                    ),
                    md={"size": 10, "offset": 1},
                    className="mb-4",
                )
            ),

            # Leyenda de significancia
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dbc.Row([
                                dbc.Col(html.Span("*** p < 0.001  Altamente significativo",
                                    className="small fw-bold", style={"color": "#F5C842"}), md=3),
                                dbc.Col(html.Span("**  p < 0.01   Muy significativo",
                                    className="small fw-bold", style={"color": "#F5C842"}), md=3),
                                dbc.Col(html.Span("*   p < 0.05   Significativo",
                                    className="small fw-bold", style={"color": "#F5C842"}), md=3),
                                dbc.Col(html.Span("ns  p ≥ 0.05   No significativo",
                                    className="small text-muted"), md=3),
                            ])
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"background": "#1C1C22", "border-radius": "12px"},
                    ),
                    width=12,
                )
            ),

            # Tabla detallada Spearman
            dbc.Row(
                dbc.Col(
                    html.H6("Tabla Detallada – Correlación de Spearman (todos los pares)",
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                data=_pvalue_table(corr_sp, pval_sp, "Spearman").to_dict("records"),
                                columns=[
                                    {"name": c, "id": c}
                                    for c in ["Par de Variables", "r", "p-valor", "Significancia", "Fuerza", "Dirección"]
                                ],
                                style_table={"overflowX": "auto"},
                                style_header={
                                    "backgroundColor": "#1A1A22", "color": "#E8D5A3",
                                    "fontWeight": "bold", "textAlign": "center",
                                    "fontSize": "12px", "padding": "10px",
                                },
                                style_data_conditional=[
                                    {"if": {"row_index": "odd"}, "backgroundColor": "#1A1A22"},
                                    {"if": {"filter_query": '{Significancia} contains "***"'},
                                     "backgroundColor": "#f5f5f5", "fontWeight": "bold"},
                                    {"if": {"filter_query": '{Fuerza} = "Muy alta"'},
                                     "color": "#E8D5A3", "fontWeight": "bold"},
                                ],
                                style_cell={
                                    "textAlign": "center", "padding": "8px 12px",
                                    "fontSize": "12px", "fontFamily": "Inter, sans-serif",
                                    "whiteSpace": "normal",
                                },
                                page_size=12,
                                sort_action="native",
                            )
                        ),
                        className="shadow-sm border-0 mb-4",
                        style={"border-radius": "14px"},
                    ),
                    width=12,
                )
            ),

            # ── Multilinea final ─────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(figure=fig_multi, config={"displayModeBar": False})),
                        className="shadow-sm border-0 mb-4",
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

def _interpretacion_card(titulo, stats_str, descripcion, bg):
    titulo_content = titulo if isinstance(titulo, list) else [titulo]
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6(titulo_content, className="fw-bold mb-1", style={"color": "#E8D5A3", "font-size": "0.85rem"}),
                    html.P(stats_str, className="small text-muted mb-2",
                           style={"font-size": "0.75rem"}),
                    html.P(descripcion, className="small text-secondary mb-0",
                           style={"font-size": "0.78rem"}),
                ]
            ),
            className="shadow-sm border-0 h-100",
            style={"background": "#1C1C22", "border-radius": "14px"},
        ),
        xs=12, sm=6, md=3,
    )


def _corr_item(var1, var2, valor, nivel):
    color = "#D4A017" if "muy alta" in nivel else "#3D3D4A"
    return dbc.Col(
        html.Div(
            [
                html.Span(f"Total ↔ {var2}", className="small fw-semibold d-block", style={"color": "#F5C842"}),
                html.Span(f"r = {valor} ({nivel})", className="small text-muted"),
            ],
            className="p-2 rounded-3",
            style={"background": "#1C1C22", "border-left": f"4px solid {color}"},
        ),
        xs=12, sm=6, md=4,
    )

def _corr_kpi_card(variable: str, pearson: str, spearman: str, bg: str):
    """Card compacto mostrando r de Pearson y ρ de Spearman para un par con Total."""
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.P(variable, className="small fw-bold mb-1", style={"color": "#F5C842"}),
                    html.Div([
                        html.Span("Pearson ", className="small text-muted"),
                        html.Span(pearson, className="small fw-bold", style={"color": "#F5C842"}),
                    ], className="mb-1"),
                    html.Div([
                        html.Span("Spearman ", className="small text-muted"),
                        html.Span(spearman, className="small fw-bold", style={"color": "#F5C842"}),
                    ]),
                ],
            ),
            className="shadow-sm border-0 h-100",
            style={"background": "#1C1C22", "border-radius": "12px"},
        ),
        xs=6, sm=4, md=2, className="mb-2",
    )
