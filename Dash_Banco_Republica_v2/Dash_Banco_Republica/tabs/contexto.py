"""tabs/contexto.py"""
from tabs.svg_icons import svg_icon
from dash import html
import dash_bootstrap_components as dbc

def layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H3("Contexto del Sistema Financiero Colombiano",
            className="fw-bold mb-1 pt-3", style={"color": "#F5C842"}), width=12)),
        dbc.Row(dbc.Col(html.P("Impacto empresarial, hogares y transmisión de política monetaria",
            className="mb-4", style={"color": "#F5C842"}), width=12)),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H5("Sistema Crediticio Colombiano", className="fw-semibold mb-3", style={"color": "#F5C842"}),
                html.P("El sistema financiero colombiano es uno de los más desarrollados de América Latina. "
                       "El Banco de la República actúa como autoridad monetaria fijando tasas de referencia "
                       "que influyen directamente en las tasas de colocación del sistema bancario, determinando "
                       "el costo del crédito para hogares y empresas.", style={"color": "#F5C842"}),
                html.P("Las modalidades de crédito analizadas (consumo, tesorería, ordinario y preferencial) "
                       "representan distintos segmentos del mercado y responden de manera diferenciada a los "
                       "ciclos económicos y decisiones de política monetaria.", style={"color": "#F5C842"}),
            ])), md=6, className="mb-3"),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H5("Impacto Empresarial", className="fw-semibold mb-3", style={"color": "#F5C842"}),
                html.P("Las empresas colombianas dependen del crédito de tesorería y ordinario para financiar "
                       "su capital de trabajo y proyectos de inversión. Variaciones en las tasas de colocación "
                       "afectan directamente:", style={"color": "#F5C842"}),
                html.Ul([
                    html.Li("El costo de financiamiento empresarial", style={"color": "#F5C842"}),
                    html.Li("La inversión y generación de empleo", style={"color": "#F5C842"}),
                    html.Li("La capacidad de expansión de las pymes", style={"color": "#F5C842"}),
                    html.Li("La rentabilidad del sector bancario", style={"color": "#F5C842"}),
                ]),
            ])), md=6, className="mb-3"),
        ], className="mb-3"),

        dbc.Row(dbc.Col(html.H5("Modalidades de Crédito Analizadas",
            className="fw-semibold mb-3", style={"color": "#F5C842"}), width=12)),
        dbc.Row([
            _credito(svg_icon('credit_card'), "Consumo",       "Financiamiento de bienes y servicios para personas naturales. Refleja el nivel de confianza del consumidor."),
            _credito(svg_icon('bank'),"Tesorería",      "Créditos de corto plazo para empresas que requieren liquidez inmediata. Altamente sensibles al mercado monetario."),
            _credito(svg_icon('box'), "Ordinarios",    "Créditos comerciales estándar para actividades productivas. Principal fuente de financiamiento empresarial."),
            _credito(svg_icon('star'), "Preferenciales","Créditos a tasas favorables para grandes empresas con bajo riesgo. Indicador del crédito corporativo."),
        ], className="g-3 mb-4"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Mecanismo de Transmisión Monetaria", className="fw-semibold mb-3", style={"color": "#F5C842"}),
            dbc.Row([_paso(n, t, d) for n, t, d in [
                ("1","Decisión del Banco de la República","Fija la tasa de intervención (referencia)"),
                ("2","Ajuste del Sistema Bancario","Los bancos adaptan sus tasas activas y pasivas"),
                ("3","Impacto en el Crédito","Cambia el costo y volumen del crédito otorgado"),
                ("4","Efecto en la Economía Real","Inversión, consumo y actividad económica"),
            ]], className="g-2"),
        ])), width=12)),
    ], fluid=True, className="px-3 py-3")


def _credito(emoji, titulo, desc):
    return dbc.Col(dbc.Card(dbc.CardBody(
        html.Div([
            # Emoji grande y visible en la parte superior
            html.Div(emoji, style={
                "font-size": "2.2rem",
                "line-height": "1",
                "margin-bottom": "10px",
                "filter": "drop-shadow(0 0 6px rgba(212,175,55,0.45))",
                "display": "block",
            }),
            # Emoji fantasma de fondo
            html.Div(emoji, style={"position": "absolute", "bottom": "6px", "right": "8px",
                                   "font-size": "3.5rem", "opacity": "0.07", "user-select": "none"}),
            html.H6(titulo, className="fw-bold mb-2", style={"color": "#F5C842"}),
            html.P(desc, className="small mb-0", style={"color": "#E8D5A3"}),
        ], style={"position": "relative", "min-height": "100px"}),
    ), style={"background": "#1C1C22", "border-radius": "12px",
              "border": "1px solid #3D2E0A"}), xs=12, sm=6, md=3)


def _paso(num, titulo, desc):
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.Div(num, className="fw-bold text-center mb-2",
                 style={"font-size": "1.4rem", "color": "#E8D5A3"}),
        html.P(titulo, className="fw-semibold small text-center mb-1", style={"color": "#F5C842"}),
        html.P(desc, className="small text-center mb-0", style={"color": "#F5C842"}),
    ])), xs=12, sm=6, md=3)
