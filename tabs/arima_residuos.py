"""
tabs/arima_residuos.py
Pestaña – Análisis de residuos del modelo ARIMA.
Refleja las celdas 88-90 del notebook EdaVis.ipynb con interpretaciones detalladas del VisBook:
  - Serie de residuos en el tiempo
  - Histograma + densidad (KDE)
  - ACF de residuos
  - Boxplot por mes (homocedasticidad)
  - Pruebas estadísticas: Shapiro-Wilk y Ljung-Box
  - Conclusión e implicaciones para el modelo
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

# ── Colores coherentes ────────────────────────────────────────────────────
COLOR_RESID   = "#D4A017"
COLOR_HIST    = "#C8963C"
COLOR_ACF_SIG = "#F5C842"
COLOR_ACF_NS  = "#3D3D4A"
COLOR_BOX     = "#E8A020"
RADIUS        = "14px"


# ── Figuras ────────────────────────────────────────────────────────────────

def _residuals_time_figure(residuos):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=residuos.index, y=residuos.values,
        mode="lines", name="Residuos",
        line=dict(color=COLOR_RESID, width=1.5),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#5A5A6E", line_width=1)
    fig.update_layout(
        title=dict(text="Serie de Residuos en el Tiempo", font=dict(color="#F5C842", size=14)),
        xaxis_title=dict(text="Fecha", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Residuo", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=50, r=20, t=50, b=40), height=280,
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )
    return fig


def _residuals_hist_figure(residuos):
    from scipy.stats import gaussian_kde
    vals = residuos.dropna().values
    kde = gaussian_kde(vals)
    x_range = np.linspace(vals.min(), vals.max(), 300)
    kde_vals = kde(x_range)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=vals, nbinsx=40, name="Frecuencia",
        marker_color=COLOR_HIST, opacity=0.7,
        histnorm="probability density",
    ))
    fig.add_trace(go.Scatter(
        x=x_range, y=kde_vals, mode="lines", name="KDE",
        line=dict(color="#F5C842", width=2),
    ))
    fig.update_layout(
        title=dict(text="Distribución de Residuos", font=dict(color="#F5C842", size=14)),
        xaxis_title="Residuo", yaxis_title=dict(text="Densidad", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        legend=dict(orientation="h", y=-0.2, font=dict(color="#F5C842", size=11), bgcolor="rgba(15,15,18,0.85)", bordercolor="#B8860B", borderwidth=1),
        margin=dict(l=50, r=20, t=50, b=55), height=280,
        barmode="overlay",
    )
    return fig


def _acf_residuals_figure(residuos, nlags=20):
    from statsmodels.tsa.stattools import acf
    vals = residuos.dropna()
    acf_vals, _ = acf(vals, nlags=nlags, alpha=0.05)
    lags = list(range(len(acf_vals)))
    conf = 1.96 / np.sqrt(len(vals))

    fig = go.Figure()
    fig.add_hline(y=0, line_color="#5A5A6E", line_width=1)
    fig.add_hrect(y0=-conf, y1=conf, fillcolor="rgba(212,160,23,0.12)", line_width=0)
    for lag, val in zip(lags, acf_vals):
        color = COLOR_ACF_SIG if abs(val) > conf else COLOR_ACF_NS
        fig.add_trace(go.Bar(x=[lag], y=[val], marker_color=color,
                             showlegend=False, width=0.6))
    fig.update_layout(
        title=dict(text="ACF de Residuos (20 lags)", font=dict(color="#F5C842", size=14)),
        xaxis_title=dict(text="Lag", font=dict(color="#CEC5A8")), yaxis_title=dict(text="Autocorrelación", font=dict(color="#CEC5A8")),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=50, r=20, t=50, b=40), height=280,
        legend=dict(
            font=dict(color="#F5C842", size=11, family="Jost, sans-serif"),
            bgcolor="rgba(15,15,18,0.88)",
            bordercolor="#B8860B", borderwidth=1
        ),
    )
    return fig


def _boxplot_mes_figure(residuos):
    # ── Winsorización: recorta outliers extremos para visualización ─────────
    # Usa IQR×3 como límite; los puntos más allá se muestran como marcadores
    # en el borde, sin distorsionar la escala del gráfico.
    vals_all = residuos.values
    Q1, Q3 = np.percentile(vals_all, 25), np.percentile(vals_all, 75)
    IQR = Q3 - Q1
    # Límite generoso: 2.5×IQR captura crisis 1998 sin destruir la escala
    cap_low  = Q1 - 2.5 * IQR
    cap_high = Q3 + 2.5 * IQR

    # Winsorizar: recortar al límite
    vals_win = np.clip(vals_all, cap_low, cap_high)

    df_r = pd.DataFrame({
        "residuos": vals_win,
        "mes": residuos.index.month,
        "fecha": residuos.index,
    })
    # Datos originales para mostrar outliers reales como puntos separados
    df_orig = pd.DataFrame({
        "residuos": vals_all,
        "mes": residuos.index.month,
        "fecha": residuos.index,
    })
    outliers_df = df_orig[
        (df_orig["residuos"] < cap_low) | (df_orig["residuos"] > cap_high)
    ]

    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    fig = go.Figure()

    # Boxplots con datos winsorizados
    for m in range(1, 13):
        subset = df_r[df_r["mes"] == m]["residuos"]
        fig.add_trace(go.Box(
            y=subset, name=meses[m - 1],
            marker_color=COLOR_BOX, showlegend=False,
            boxmean=True,
            line=dict(color=COLOR_BOX, width=1.5),
        ))

    # Outliers reales marcados como puntos distintos con anotación
    if not outliers_df.empty:
        for _, row in outliers_df.iterrows():
            # Mostrar en el borde del eje con valor real en tooltip
            y_display = cap_high if row["residuos"] > 0 else cap_low
            fig.add_trace(go.Scatter(
                x=[meses[row["mes"] - 1]],
                y=[y_display],
                mode="markers+text",
                marker=dict(
                    symbol="triangle-up" if row["residuos"] > 0 else "triangle-down",
                    size=12,
                    color="#e8c96a",
                    line=dict(color="#9a7733", width=1.5),
                ),
                text=[f"  {row['residuos']:.1f}"],
                textposition="middle right",
                textfont=dict(color="#e8c96a", size=10),
                hovertemplate=(
                    f"<b>{row['fecha'].strftime('%b %Y')}</b><br>"
                    f"Residuo real: <b>{row['residuos']:.4f}</b><br>"
                    f"<i>(outlier extremo — acotado en gráfico)</i>"
                    "<extra></extra>"
                ),
                showlegend=False,
            ))

    fig.add_hline(y=0, line_dash="dash", line_color="#5A5A6E", line_width=1.5)

    # Nota al pie sobre outliers omitidos
    n_out = len(outliers_df)
    note = (
        f"▲ {n_out} outlier{'s' if n_out != 1 else ''} extremo{'s' if n_out != 1 else ''} "
        f"acotado{'s' if n_out != 1 else ''} en eje (valores reales visibles al pasar el cursor)"
        if n_out > 0 else ""
    )

    fig.update_layout(
        title=dict(text="Homocedasticidad – Boxplot de Residuos por Mes",
                   font=dict(color="#F5C842", size=14)),
        xaxis=dict(title=dict(text="Mes", font=dict(color="#CEC5A8", size=12)),
                   tickfont=dict(color="#CEC5A8", size=12), gridcolor="#2A2A30"),
        yaxis=dict(title=dict(text="Residuo", font=dict(color="#CEC5A8", size=12)),
                   tickfont=dict(color="#CEC5A8", size=11), gridcolor="#2A2A30",
                   zeroline=True, zerolinecolor="#5A5A6E",
                   range=[cap_low * 1.15, cap_high * 1.15]),
        paper_bgcolor="#1C1C22", plot_bgcolor="#141418",
        margin=dict(l=60, r=30, t=60, b=70), height=460,
        showlegend=False,
        annotations=[dict(
            text=note, showarrow=False,
            xref="paper", yref="paper", x=0, y=-0.14,
            font=dict(color="#7a6f5a", size=10), align="left",
        )] if note else [],
    )
    return fig


# ── Tarjetas de pruebas estadísticas ──────────────────────────────────────

def _stat_test_card(titulo, estadistico, p_valor, hipotesis, conclusion, pasa,
                    interpretacion_detallada=""):
    icono      = svg_icon('check_circle', color='#4caf7d') if pasa else svg_icon('warning', color='#d4a04a')
    pval_color = "#27ae60" if pasa else "#dc3545"
    titulo_content = titulo if isinstance(titulo, list) else [titulo]
    conclusion_content = conclusion if isinstance(conclusion, list) else [conclusion]
    body_parts = [
        html.H6([icono] + titulo_content, className="fw-bold mb-3",
                style={"color": "#F5C842"}),
        dbc.Row([
            dbc.Col([
                html.P("Estadístico", className="small text-muted mb-0"),
                html.H5(f"{estadistico:.4f}", className="fw-bold mb-0",
                        style={"color": "#1a1a2e"}),
            ], width=6),
            dbc.Col([
                html.P("p-valor", className="small text-muted mb-0"),
                html.H5(f"{p_valor:.4f}", className="fw-bold mb-0",
                        style={"color": pval_color}),
            ], width=6),
        ], className="mb-3"),
        html.Hr(className="my-2"),
        html.P(hipotesis, className="small text-muted fst-italic mb-1"),
        html.P(conclusion, className="small fw-semibold mb-0",
               style={"color": pval_color}),
    ]
    if interpretacion_detallada:
        body_parts += [
            html.Hr(className="my-2"),
            html.P(interpretacion_detallada, className="small text-secondary mb-0",
                   style={"text-align": "justify"}),
        ]
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(body_parts),
            className="shadow-sm border-0 h-100",
            style={"background": "#1C1C22", "border-radius": RADIUS},
        ),
        md=6,
    )


# ── Tarjeta de interpretación de supuesto ─────────────────────────────────

def _supuesto_card(titulo, icono, color_borde, texto):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H6([icono, " ", titulo], className="fw-bold mb-2",
                        style={"color": "#F5C842"}),
                html.P(texto, className="small text-secondary mb-0",
                       style={"text-align": "justify"}),
            ]),
            className="shadow-sm border-0 h-100",
            style={"background": "#1C1C22", "border-radius": RADIUS,
                   "border-top": f"4px solid {color_borde}"},
        ),
        xs=12, sm=6, md=3, className="mb-3",
    )


# ── Layout ────────────────────────────────────────────────────────────────

def layout():
    df    = DF.copy()
    res   = load_model_results()
    arima = res.get("arima", {})
    resid_data = arima.get("residuos", {})

    resid_index  = pd.to_datetime(resid_data.get("index", []))
    resid_values = np.array(resid_data.get("values", []))
    residuos = pd.Series(resid_values, index=resid_index, name="Residuos")

    sw_stat    = resid_data.get("shapiro_stat",   0.0)
    sw_p       = resid_data.get("shapiro_p",       0.0)
    lb_stat    = resid_data.get("ljungbox_stat",  0.0)
    lb_p       = resid_data.get("ljungbox_p",      0.0)
    resid_mean = resid_data.get("media",           0.0)
    bp_lm_stat = resid_data.get("bp_lm_stat",     0.0)
    bp_lm_p    = resid_data.get("bp_lm_p",        0.0)
    bp_f_stat  = resid_data.get("bp_f_stat",      0.0)
    bp_f_p     = resid_data.get("bp_f_p",         0.0)

    fig_time = _residuals_time_figure(residuos)
    fig_hist = _residuals_hist_figure(residuos)
    fig_acf  = _acf_residuals_figure(residuos)
    fig_box  = _boxplot_mes_figure(residuos)

    order_str = arima.get("order_str", "ARIMA")

    # Determine overall health
    ambos_ok = (sw_p >= 0.05 and lb_p >= 0.05)
    alguno_falla = (sw_p < 0.05 or lb_p < 0.05)

    return dbc.Container([

        # ── Encabezado ────────────────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H3(f"Análisis de Residuos – {order_str}",
                    className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row(dbc.Col(
            html.P(
                "Verificación de supuestos: media cero · normalidad (Shapiro-Wilk) · "
                "independencia (Ljung-Box) · homocedasticidad (boxplot mensual)",
                className="text-muted mb-4",
            ),
            width=12,
        )),

        # ── Por qué analizar residuos ─────────────────────────────────
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5([svg_icon('info'), " ¿Por qué analizar los residuos?"],
                            className="fw-semibold mb-3", style={"color": "#F5C842"}),
                    html.P(
                        "Un modelo ARIMA bien ajustado debe producir residuos que se comporten "
                        "como ruido blanco: media cero, varianza constante, sin autocorrelación "
                        "y con distribución aproximadamente normal. Si alguno de estos supuestos "
                        "se viola, el modelo no ha capturado toda la estructura de la serie y "
                        "sus predicciones no son completamente confiables. El análisis de residuos "
                        "es, en esencia, una auditoría estadística del modelo: nos dice cuánto "
                        "dejó de capturar y en qué dirección mejorar.",
                        className="text-secondary mb-0",
                        style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0 mb-4",
                style={"background": "#1C1C22", "border-radius": RADIUS},
            ),
            width=12,
        )),

        # ── Los 4 supuestos del ruido blanco ─────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('clipboard'), " Los Cuatro Supuestos del Ruido Blanco"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            _supuesto_card("Media Cero", svg_icon('n1'), "#27ae60",
                "Los residuos deben tener esperanza matemática igual a cero. Si la media es "
                "distinta de cero, el modelo presenta sesgo sistemático: siempre sobreestima o "
                "subestima. Se verifica calculando directamente la media aritmética de los residuos."),
            _supuesto_card("Normalidad", svg_icon('n2'), "#D4A017",
                "Los residuos deben seguir una distribución normal. Este supuesto es clave para "
                "que los intervalos de confianza del pronóstico sean válidos. Se verifica con la "
                "prueba Shapiro-Wilk (H₀: los residuos son normales) y visualmente con el histograma + KDE."),
            _supuesto_card("Independencia", svg_icon('n3'), "#e74c3c",
                "Los residuos no deben presentar autocorrelación: el error en un periodo no debe "
                "predecir el error en el siguiente. Si hay autocorrelación, el modelo dejó "
                "estructura sin capturar. Se verifica con la prueba Ljung-Box y el correlograma ACF."),
            _supuesto_card("Homocedasticidad", svg_icon('n4'), "#e67e22",
                "La varianza de los residuos debe ser constante a lo largo del tiempo, sin "
                "expandirse ni contraerse en ciertos periodos. Se verifica visualmente con el "
                "gráfico de serie temporal y el boxplot mensual, y formalmente con la prueba "
                "Breusch–Pagan (H₀: varianza constante). Un p-valor < 0.05 indica "
                "heterocedasticidad significativa."),
        ], className="g-3 mb-4"),

        # ── Media de residuos ─────────────────────────────────────────
        dbc.Row(dbc.Col(
            dbc.Alert([
                html.Strong([svg_icon('n1'), " Media de residuos: "]),
                f"{resid_mean:.6f}  ",
                html.Span(
                    "≈ 0  ✓  (ausencia de sesgo sistemático — supuesto cumplido)"
                    if abs(resid_mean) < 0.1 else
                    "⚠  La media no es cero; podría existir sesgo sistemático.",
                    className="ms-2",
                ),
            ], color="success" if abs(resid_mean) < 0.1 else "warning",
               className="py-2 mb-1"),
            width=12,
        )),
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    html.P(
                        f"La media de los residuos es {resid_mean:.6f}, un valor prácticamente "
                        "indistinguible de cero. Esto indica que el modelo no presenta sesgo "
                        "sistemático: en promedio, las predicciones no sobreestiman ni subestiman "
                        "de forma consistente la variable objetivo. Este es el único supuesto del "
                        "ruido blanco que el modelo cumple satisfactoriamente.",
                        className="small text-secondary mb-0",
                        style={"text-align": "justify"},
                    )
                ),
                className="shadow-sm border-0 mb-4",
                style={"background": "#f0fff4", "border-radius": RADIUS},
            ),
            width=12,
        )),

        # ── Serie de residuos + Histograma ────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('n2'), " & ", svg_icon('n3'), " Comportamiento Visual de los Residuos"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_time,
                                           config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-4",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_hist,
                                           config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-4",
            ),
        ]),

        # Interpretaciones visuales
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6([svg_icon('search'), " Serie de Residuos en el Tiempo"],
                                className="fw-bold mb-2", style={"color": "#F5C842"}),
                        html.P(
                            "La serie de residuos debe oscilar aleatoriamente alrededor del cero "
                            "sin patrones evidentes de tendencia, ciclos ni expansión de la "
                            "varianza. Si se observan clusters de errores grandes (grupos de "
                            "residuos de similar magnitud), esto sugiere heterocedasticidad. "
                            "Si hay periodos de errores sistemáticamente positivos o negativos, "
                            "indica que el modelo no capturó completamente la dinámica de la serie "
                            "en ese período — frecuentemente asociado a choques externos como la "
                            "crisis de 1998-1999 o la pandemia de 2020.",
                            className="small text-secondary mb-0",
                            style={"text-align": "justify"},
                        ),
                    ]),
                    className="shadow-sm border-0 mb-3",
                    style={"background": "#141418", "border-radius": RADIUS},
                ),
                md=6,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6([svg_icon('search'), " Distribución de Residuos (Histograma + KDE)"],
                                className="fw-bold mb-2", style={"color": "#F5C842"}),
                        html.P(
                            "El histograma con la curva de densidad (KDE) permite inspeccionar "
                            "visualmente la forma de la distribución de los residuos. Una "
                            "distribución normal se manifestaría como una campana de Gauss "
                            "simétrica centrada en cero. Colas pesadas (curtosis alta), asimetría "
                            "o multimodalidad indican violación del supuesto de normalidad. La "
                            "prueba Shapiro-Wilk formaliza este diagnóstico visual con un estadístico "
                            "y p-valor que permiten una conclusión objetiva.",
                            className="small text-secondary mb-0",
                            style={"text-align": "justify"},
                        ),
                    ]),
                    className="shadow-sm border-0 mb-3",
                    style={"background": "#141418", "border-radius": RADIUS},
                ),
                md=6,
            ),
        ]),

        # ── ACF de residuos + Boxplot mensual ─────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('n3'), " & ", svg_icon('n4'), " Independencia y Homocedasticidad"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_acf,
                                           config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-4",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig_box,
                                           config={"displayModeBar": False})),
                    className="shadow-sm border-0", style={"border-radius": RADIUS},
                ),
                md=6, className="mb-4",
            ),
        ]),

        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6([svg_icon('search'), " ACF de Residuos — Independencia"],
                                className="fw-bold mb-2", style={"color": "#F5C842"}),
                        html.P(
                            "El correlograma de los residuos debe mostrar todos los lags dentro "
                            "de las bandas de confianza del 95% (zona sombreada). Las barras "
                            "moradas indican rezagos estadísticamente significativos: si aparecen "
                            "varios rezagos significativos fuera de las bandas, confirma que el "
                            "modelo dejó autocorrelación sin capturar, es decir, que los errores "
                            "no son independientes entre sí. Este hallazgo respalda la conclusión "
                            "de la prueba Ljung-Box: existe estructura en los residuos que el "
                            "modelo ARIMA no pudo modelar.",
                            className="small text-secondary mb-0",
                            style={"text-align": "justify"},
                        ),
                    ]),
                    className="shadow-sm border-0 mb-3",
                    style={"background": "#141418", "border-radius": RADIUS},
                ),
                md=6,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6([svg_icon('search'), " Boxplot Mensual — Homocedasticidad"],
                                className="fw-bold mb-2", style={"color": "#F5C842"}),
                        html.P(
                            "El boxplot de residuos agrupados por mes permite evaluar si la "
                            "varianza se mantiene estable a lo largo del año. Si las cajas tienen "
                            "tamaños similares en todos los meses (homocedasticidad), el modelo "
                            "presenta errores uniformes sin estacionalidad en la varianza. "
                            "Si algunos meses tienen cajas significativamente más anchas o con "
                            "más valores atípicos (outliers), podría existir heterocedasticidad "
                            "estacional, típica de series financieras con mayor volatilidad en "
                            "ciertos periodos del año.",
                            className="small text-secondary mb-0",
                            style={"text-align": "justify"},
                        ),
                    ]),
                    className="shadow-sm border-0 mb-3",
                    style={"background": "#141418", "border-radius": RADIUS},
                ),
                md=6,
            ),
        ]),

        # ── Pruebas estadísticas ──────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('microscope'), " Pruebas Estadísticas sobre Residuos"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            _stat_test_card(
                titulo=[svg_icon('n2'), " Normalidad – Shapiro-Wilk"],
                estadistico=sw_stat,
                p_valor=sw_p,
                hipotesis="H₀: Los residuos siguen una distribución normal",
                conclusion=(
                    "No se rechaza H₀ → residuos normales (p ≥ 0.05)"
                    if sw_p >= 0.05 else
                    "Se rechaza H₀ → residuos NO son normales (p < 0.05)"
                ),
                pasa=(sw_p >= 0.05),
                interpretacion_detallada=(
                    "El estadístico W de Shapiro-Wilk mide qué tan bien se ajustan los residuos "
                    "a una distribución normal (W = 1 sería perfectamente normal). Un p-valor "
                    f"{'≥ 0.05 indica que no hay evidencia suficiente para rechazar la normalidad, lo que valida los intervalos de confianza del pronóstico.' if sw_p >= 0.05 else '< 0.05 significa que los residuos presentan una distribución significativamente distinta de la normal (colas más pesadas o asimetría), invalidando los intervalos de confianza del pronóstico y sugiriendo que el modelo no capturó completamente la distribución real de los errores. Este resultado es frecuente en series financieras con eventos extremos como las crisis de 1998-1999 y la pandemia 2020.'}"
                ),
            ),
            _stat_test_card(
                titulo=[svg_icon('n3'), " Independencia – Ljung-Box (lag 10)"],
                estadistico=lb_stat,
                p_valor=lb_p,
                hipotesis="H₀: Los residuos no presentan autocorrelación",
                conclusion=(
                    "No se rechaza H₀ → residuos independientes (p ≥ 0.05)"
                    if lb_p >= 0.05 else
                    "Se rechaza H₀ → autocorrelación significativa (p < 0.05)"
                ),
                pasa=(lb_p >= 0.05),
                interpretacion_detallada=(
                    "La prueba de Ljung-Box evalúa conjuntamente si alguno de los primeros 10 "
                    "rezagos de los residuos presenta autocorrelación significativa. Un p-valor "
                    f"{'≥ 0.05 indica que los residuos son estadísticamente independientes, confirmando que el modelo capturó adecuadamente la estructura de autocorrelación de la serie.' if lb_p >= 0.05 else '< 0.05 revela que existe autocorrelación significativa en los residuos: los errores del modelo no son independientes entre sí, lo que significa que los rezagos de los residuos aún contienen información predictiva que el modelo ARIMA no aprovechó. Esto sugiere que el orden q o p podría ser mayor, o que la serie presenta patrones no lineales que escapan al enfoque ARIMA clásico.'}"
                ),
            ),
        ], className="g-3 mb-4"),

        # ── Prueba Breusch-Pagan ──────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('microscope'), " Prueba de Homocedasticidad – Breusch–Pagan"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            _stat_test_card(
                titulo=[svg_icon('n4'), " Homocedasticidad – Breusch–Pagan (LM)"],
                estadistico=bp_lm_stat,
                p_valor=bp_lm_p,
                hipotesis="H₀: Los residuos presentan varianza constante (homocedasticidad)",
                conclusion=(
                    "No se rechaza H₀ → varianza constante (p ≥ 0.05)"
                    if bp_lm_p >= 0.05 else
                    "Se rechaza H₀ → heterocedasticidad detectada (p < 0.05)"
                ),
                pasa=(bp_lm_p >= 0.05),
                interpretacion_detallada=(
                    "La prueba Breusch–Pagan evalúa si la varianza de los residuos es constante "
                    "regresando los residuos al cuadrado sobre los valores ajustados. "
                    "El estadístico LM sigue una distribución χ² bajo H₀. "
                    f"{'Un p-valor ≥ 0.05 indica que no hay evidencia de heterocedasticidad: la varianza es homogénea.' if bp_lm_p >= 0.05 else 'Un p-valor < 0.05 confirma heterocedasticidad: la varianza de los residuos varía sistemáticamente con los valores ajustados, lo que es típico en series financieras con episodios de alta volatilidad (crisis 1998-1999, pandemia 2020). Esto invalida los intervalos de confianza clásicos y sugiere usar errores estándar robustos o modelos GARCH.'} "
                    f"Estadístico F complementario: {bp_f_stat:.4f} (p = {bp_f_p:.4f})."
                ),
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6([svg_icon('info'), " ¿Qué mide Breusch–Pagan?"],
                                className="fw-bold mb-3", style={"color": "#F5C842"}),
                        html.P(
                            "La prueba de Breusch–Pagan (1979) evalúa formalmente si la varianza "
                            "de los errores del modelo es constante (homocedasticidad) o si varía "
                            "en función de los valores ajustados (heterocedasticidad). Funciona "
                            "regresando los residuos al cuadrado sobre las variables explicativas "
                            "y verificando si esa regresión auxiliar tiene poder explicativo "
                            "significativo.",
                            className="small text-secondary mb-2",
                            style={"text-align": "justify"},
                        ),
                        html.Hr(className="my-2"),
                        dbc.Row([
                            dbc.Col([
                                html.P("Estadístico F", className="small text-muted mb-0"),
                                html.H5(f"{bp_f_stat:.4f}", className="fw-bold mb-0",
                                        style={"color": "#1a1a2e"}),
                            ], width=6),
                            dbc.Col([
                                html.P("p-valor F", className="small text-muted mb-0"),
                                html.H5(f"{bp_f_p:.4f}", className="fw-bold mb-0",
                                        style={"color": "#27ae60" if bp_f_p >= 0.05 else "#dc3545"}),
                            ], width=6),
                        ]),
                        html.Hr(className="my-2"),
                        html.P(
                            "Consecuencia práctica: si se detecta heterocedasticidad, los "
                            "intervalos de confianza del pronóstico ARIMA subestiman la "
                            "incertidumbre real en periodos de alta volatilidad. Se recomienda "
                            "complementar con modelos ARCH/GARCH o aplicar transformaciones "
                            "logarítmicas para estabilizar la varianza.",
                            className="small text-secondary mb-0",
                            style={"text-align": "justify"},
                        ),
                    ]),
                    className="shadow-sm border-0 h-100",
                    style={"background": "#1C1C22", "border-radius": RADIUS},
                ),
                md=6,
            ),
        ], className="g-3 mb-4"),

        # ── Resumen de supuestos ──────────────────────────────────────
        dbc.Row(dbc.Col(
            html.H5([svg_icon('bar_chart'), " Resumen del Diagnóstico de Supuestos"],
                    className="fw-semibold mb-3", style={"color": "#F5C842"}),
            width=12,
        )),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.Span([svg_icon('check_circle', color='#4caf7d')], style={"font-size": "1.5rem"}),
                            html.Span(" Media ≈ 0", className="fw-bold ms-2"),
                        ], className="mb-1"),
                        html.P("Ausencia de sesgo sistemático", className="small text-muted mb-0"),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={"background": "#f0fff4", "border-radius": RADIUS,
                           "border-top": "4px solid #27ae60"},
                ),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.Span([svg_icon('check_circle', color='#4caf7d')] if sw_p >= 0.05 else [svg_icon('warning', color='#d4a04a')], style={"font-size": "1.5rem"}),
                            html.Span(" Normalidad", className="fw-bold ms-2"),
                        ], className="mb-1"),
                        html.P(
                            f"Shapiro-Wilk p = {sw_p:.4f} {'✓' if sw_p >= 0.05 else '✗'}",
                            className="small text-muted mb-0",
                        ),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={
                        "background": "#f0fff4" if sw_p >= 0.05 else "#fff8e1",
                        "border-radius": RADIUS,
                        "border-top": f"4px solid {'#27ae60' if sw_p >= 0.05 else '#e67e22'}",
                    },
                ),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.Span([svg_icon('check_circle', color='#4caf7d')] if lb_p >= 0.05 else [svg_icon('warning', color='#d4a04a')], style={"font-size": "1.5rem"}),
                            html.Span(" Independencia", className="fw-bold ms-2"),
                        ], className="mb-1"),
                        html.P(
                            f"Ljung-Box p = {lb_p:.4f} {'✓' if lb_p >= 0.05 else '✗'}",
                            className="small text-muted mb-0",
                        ),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={
                        "background": "#f0fff4" if lb_p >= 0.05 else "#fff8e1",
                        "border-radius": RADIUS,
                        "border-top": f"4px solid {'#27ae60' if lb_p >= 0.05 else '#e67e22'}",
                    },
                ),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.Span([svg_icon('check_circle', color='#4caf7d')] if bp_lm_p >= 0.05 else [svg_icon('warning', color='#d4a04a')], style={"font-size": "1.5rem"}),
                            html.Span(" Homocedasticidad", className="fw-bold ms-2"),
                        ], className="mb-1"),
                        html.P(
                            f"Breusch–Pagan p = {bp_lm_p:.4f} {'✓' if bp_lm_p >= 0.05 else '✗'}",
                            className="small text-muted mb-0",
                        ),
                    ]),
                    className="shadow-sm border-0 text-center h-100",
                    style={
                        "background": "#f0fff4" if bp_lm_p >= 0.05 else "#fff8e1",
                        "border-radius": RADIUS,
                        "border-top": f"4px solid {'#27ae60' if bp_lm_p >= 0.05 else '#e67e22'}",
                    },
                ),
                xs=6, md=3, className="mb-3",
            ),
        ]),

        # ── Conclusión ────────────────────────────────────────────────
        dbc.Row(dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5([svg_icon('pin'), " Conclusión del Diagnóstico de Residuos"],
                            className="fw-semibold mb-2", style={"color": "#F5C842"}),
                    html.P(
                        f"El análisis de residuos del modelo {order_str} revela un diagnóstico "
                        "mixto con implicaciones claras para la confiabilidad del modelo. "
                        "Por un lado, la media de los residuos es prácticamente cero, lo que "
                        "confirma la ausencia de sesgo sistemático: el modelo no sobreestima "
                        "ni subestima de forma consistente. Sin embargo, las pruebas estadísticas "
                        "evidencian limitaciones importantes: ",
                        className="text-secondary mb-2",
                        style={"text-align": "justify"},
                    ),
                    html.Ul([
                        html.Li(
                            f"La prueba Shapiro-Wilk (p = {sw_p:.4f}) "
                            + ("no rechaza la normalidad, lo que valida los intervalos de confianza del pronóstico."
                               if sw_p >= 0.05 else
                               "rechaza la hipótesis de normalidad (p < 0.05), indicando que los residuos presentan "
                               "colas más pesadas de lo esperado, probablemente asociadas a periodos de alta volatilidad "
                               "en el mercado financiero colombiano (crisis 1998-1999, pandemia 2020)."),
                            className="small text-secondary mb-2",
                        ),
                        html.Li(
                            f"La prueba Ljung-Box (p = {lb_p:.4f}) "
                            + ("no detecta autocorrelación significativa, confirmando que los residuos son independientes."
                               if lb_p >= 0.05 else
                               "detecta autocorrelación significativa (p < 0.05), lo que indica que el modelo dejó "
                               "estructura temporal sin capturar. Los rezagos significativos en la ACF de residuos "
                               "confirman que los errores no son completamente aleatorios."),
                            className="small text-secondary mb-2",
                        ),
                        html.Li(
                            f"La prueba Breusch–Pagan (p = {bp_lm_p:.4f}) "
                            + ("no detecta heterocedasticidad: la varianza de los residuos es constante."
                               if bp_lm_p >= 0.05 else
                               "detecta heterocedasticidad significativa (p < 0.05): la varianza de los residuos varía "
                               "con los valores ajustados, posiblemente asociada a periodos de alta volatilidad financiera. "
                               "Esto sugiere que los intervalos de confianza del pronóstico subestiman la incertidumbre real."),
                            className="small text-secondary mb-2",
                        ),
                    ], style={"padding-left": "1.5rem"}),
                    html.P(
                        "En conjunto, los residuos no se comportan plenamente como ruido blanco. "
                        "Esto significa que el modelo ARIMA proporciona predicciones orientativas "
                        "útiles para identificar la tendencia general, pero con limitada capacidad "
                        "para capturar la variabilidad puntual de las tasas de colocación. "
                        "Se recomienda explorar modelos más flexibles, como Máquinas de Soporte "
                        "Vectorial (SVM) o redes neuronales LSTM, que puedan capturar relaciones "
                        "no lineales y mayor complejidad en la dinámica de la serie.",
                        className="small text-secondary mb-0",
                        style={"text-align": "justify"},
                    ),
                ]),
                className="shadow-sm border-0",
                style={
                    "background": "#fff3cd" if alguno_falla else "#d4edda",
                    "border-radius": RADIUS,
                    "border-left": "5px solid #e67e22"
                          if alguno_falla else "5px solid #27ae60",
                },
            ),
            width=12,
        )),

    ], fluid=True, className="px-3 py-3")
