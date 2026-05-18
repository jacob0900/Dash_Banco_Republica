"""tabs/introduccion.py"""
from tabs.svg_icons import svg_icon
from dash import html
import dash_bootstrap_components as dbc

GITHUB_URL     = "https://github.com/tu-usuario/tu-repositorio"
LINKEDIN_URL_1 = "https://www.linkedin.com/in/jacobo-londo%C3%B1o-baquero-a2b86733a/"
LINKEDIN_URL_2 = "https://www.linkedin.com/in/jesus-david-barrios-97181b337/"

def layout():
    return dbc.Container([

        dbc.Row(dbc.Col(html.Div([
            html.H2("Análisis de Tasas de Interés de Colocación",
                    className="display-6 fw-bold text-center", style={"color": "#F5C842"}),
            html.P("Banco de la República de Colombia · Series históricas mensuales 1998 – 2025",
                   className="text-center fs-5 mb-0", style={"color": "#F5C842"}),
        ], className="py-4"), width=12), className="mb-2"),

        dbc.Row([
            dbc.Col([
                html.H4("Descripción del Proyecto", className="fw-bold mb-3",
                        style={"color": "#E8D5A3", "font-size": "1.25rem",
                               "border-bottom": "2px solid #B8860B", "padding-bottom": "8px"}),
                html.P(["El análisis de las tasas de colocación y los créditos en Colombia constituye "
                        "un insumo fundamental para comprender la dinámica del sistema financiero y "
                        "la transmisión de la política monetaria. El Banco de la República recopila y "
                        "publica series estadísticas históricas que permiten estudiar la evolución de "
                        "estas variables desde finales del siglo XX ",
                        html.Span("(Banco de la República, 2024).", className="fst-italic")],
                       style={"color": "#E8D5A3", "font-size": "1.05rem", "line-height": "1.9", "text-align": "justify"}),
                html.P(["Las tasas de interés de colocación reflejan las decisiones de política "
                        "monetaria y las condiciones de liquidez en el mercado financiero. La "
                        "variabilidad de estas tasas está asociada con ciclos de expansión y "
                        "contracción del crédito, afectando la actividad económica y el acceso "
                        "al financiamiento ",
                        html.Span("(Clavijo, 2019; Villar & Salamanca, 2021).", className="fst-italic")],
                       style={"color": "#E8D5A3", "font-size": "1.05rem", "line-height": "1.9", "text-align": "justify"}),
                html.P(["La predicción de series financieras mediante modelos como ARIMA ha sido "
                        "documentada como herramienta eficaz para capturar patrones temporales en "
                        "tasas de interés ",
                        html.Span("(Box & Jenkins, 1976; Hamilton, 1994).", className="fst-italic"),
                        " El objetivo es predecir la Tasa de Colocación Total mediante técnicas "
                        "de series de tiempo, aportando evidencia sobre los mecanismos de "
                        "transmisión de la política monetaria en Colombia."],
                       style={"color": "#E8D5A3", "font-size": "1.05rem", "line-height": "1.9", "text-align": "justify"}),
                html.P(["Los datos provienen del sistema estadístico oficial del Banco de la República "
                        "y comprenden 330 observaciones mensuales desde marzo de 1998 hasta agosto de 2025 ",
                        html.Span("(Urrutia & Namen, 2012).", className="fst-italic")],
                       className="mb-0",
                       style={"color": "#E8D5A3", "font-size": "1.05rem", "line-height": "1.9", "text-align": "justify"}),
            ], md=7, className="pe-4 pt-4 pb-3"),

            dbc.Col([
                html.H2("ANÁLISIS DE TASAS DE INTERÉS DE COLOCACIÓN",
                        style={"color": "#E8D5A3", "font-size": "1.6rem", "font-weight": "800",
                               "line-height": "1.3", "text-align": "right"}),
                html.P("EN EL SISTEMA FINANCIERO COLOMBIANO",
                       style={"color": "#E8D5A3", "font-size": "0.95rem", "font-weight": "700",
                              "letter-spacing": "1px", "text-align": "right", "margin-top": "4px"}),
                html.Hr(style={"border-color": "#000000", "border-width": "2px", "margin": "16px 0"}),
                html.P("Banco de la República de Colombia",
                       style={"text-align": "right", "color": "#E8D5A3", "font-size": "0.95rem", "font-weight": "600"}),
                html.P("Series históricas mensuales · 1998 – 2025",
                       style={"text-align": "right", "color": "#E8D5A3", "font-size": "0.88rem", "margin-top": "-8px"}),
                html.Hr(style={"border-color": "#000000", "margin": "16px 0"}),
                html.P("Acceso y Recursos", className="fw-bold text-end mb-2",
                       style={"color": "#E8D5A3", "font-size": "0.85rem", "text-transform": "uppercase", "letter-spacing": "0.5px"}),
                html.Div([
                    _boton(svg_icon('link'), "Repositorio GitHub", GITHUB_URL),
                    _boton("in", "LinkedIn — Jacobo Londoño", LINKEDIN_URL_1),
                    _boton("in", "LinkedIn — Jesús David Barrios", LINKEDIN_URL_2),
                ], className="d-flex flex-column gap-2"),
            ], md=5, className="ps-4 pt-4 pb-3", style={"border-left": "1.5px solid #000000"}),
        ], className="mb-4 mt-2",
           style={"background": "#1C1C22", "border-radius": "10px", "border": "1.5px solid #000000"}),

        # KPIs
        dbc.Row([
            _kpi(svg_icon('calendar'), "Período de Análisis", "1998 – 2025"),
            _kpi(svg_icon('bar_chart'), "Frecuencia de Datos", "Mensual"),
            _kpi(svg_icon('database'), "Observaciones",       "330 registros"),
            _kpi(svg_icon('trending_up'), "Variables",           "7 series financieras"),
        ], className="g-3 mb-4"),

        # Referencias
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Referencias Bibliográficas", className="fw-bold mb-3",
                    style={"color": "#E8D5A3", "text-transform": "uppercase", "letter-spacing": "0.5px"}),
            html.Ul([
                html.Li("Banco de la República. (2024). Series estadísticas de tasas de interés de colocación. banrep.gov.co",
                        style={"font-size": "0.95rem", "color": "#E8D5A3", "line-height": "1.7", "margin-bottom": "6px"}),
                html.Li("Box, G. E. P., & Jenkins, G. M. (1976). Time Series Analysis: Forecasting and Control. Holden-Day.",
                        style={"font-size": "0.95rem", "color": "#E8D5A3", "line-height": "1.7", "margin-bottom": "6px"}),
                html.Li("Clavijo, S. (2019). Política monetaria y transmisión crediticia en Colombia. ANIF.",
                        style={"font-size": "0.95rem", "color": "#E8D5A3", "line-height": "1.7", "margin-bottom": "6px"}),
                html.Li("Hamilton, J. D. (1994). Time Series Analysis. Princeton University Press.",
                        style={"font-size": "0.95rem", "color": "#E8D5A3", "line-height": "1.7", "margin-bottom": "6px"}),
                html.Li("Urrutia, M., & Namen, O. M. (2012). Historia del crédito en Colombia en el siglo XX. Borradores de Economía, No. 724.",
                        style={"font-size": "0.95rem", "color": "#E8D5A3", "line-height": "1.7", "margin-bottom": "6px"}),
                html.Li("Villar, L., & Salamanca, D. (2021). Transmisión de la política monetaria al crédito bancario en Colombia. Ensayos sobre Política Económica, 39(89), 1–22.",
                        style={"font-size": "0.95rem", "color": "#E8D5A3", "line-height": "1.7"}),
            ], className="ps-3 mb-0"),
        ])), width=12)),

    ], fluid=True, className="px-3 py-3")


def _boton(icono, texto, url):
    return html.A(html.Div([
        html.Span(icono, style={"font-size": "1.1rem", "font-weight": "800",
                                "width": "32px", "display": "inline-block",
                                "text-align": "center", "color": "#E8D5A3"}),
        html.Span(texto, style={"font-size": "0.9rem", "font-weight": "600", "color": "#E8D5A3"}),
    ], style={"display": "flex", "align-items": "center", "gap": "10px",
              "padding": "9px 16px", "background": "#232329",
              "border-radius": "8px", "border": "1.5px solid #000000", "cursor": "pointer"}),
    href=url, target="_blank", style={"text-decoration": "none"})


def _kpi(emoji, titulo, valor):
    return dbc.Col(dbc.Card(dbc.CardBody(
        html.Div([
            # Emoji como fondo/marca de agua
            html.Div(emoji, style={"position":"absolute","bottom":"8px","right":"12px","opacity":"0.15","user-select":"none","line-height":"1"}),
            html.P(titulo, className="fw-semibold mb-1",
                   style={"font-size": "0.82rem", "text-transform": "uppercase",
                          "letter-spacing": "0.4px", "color": "#E8D5A3"}),
            html.H5(valor, className="fw-bold mb-0 font-monospace", style={"color": "#F5C842", "font-size": "1.2rem"}),
        ], style={"position": "relative", "min-height": "72px"}),
    ), style={"background": "#1C1C22", "border": "1.5px solid #000000", "border-radius": "10px"}),
    xs=12, sm=6, md=3)
