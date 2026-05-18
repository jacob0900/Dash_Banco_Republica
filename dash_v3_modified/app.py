"""
app.py – Dashboard principal de Análisis de Tasas de Interés (Colocación)
Banco de la República de Colombia · 1998-2025
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

from tabs import (
    introduccion, contexto, problema, objetivos,
    marco_teorico, metodologia, resultados,
    prediccion, conclusiones,
    arima_modelo, arima_residuos, rolling,
)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Fira+Code:wght@400;500&family=Jost:wght@300;400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="Tasas de Colocación – Banco de la República",
)

server = app.server

TABS = [
    ("tab-introduccion",  "Introducción"),
    ("tab-contexto",      "Contexto"),
    ("tab-problema",      "Problema"),
    ("tab-objetivos",     "Objetivos"),
    ("tab-marco",         "Marco Teórico"),
    ("tab-metodologia",   "Metodología"),
    ("tab-resultados",    "Resultados EDA"),
    ("tab-prediccion",    "Estacionariedad"),
    ("tab-arima-modelo",  "Modelo ARIMA"),
    ("tab-arima-residuos", "Residuos ARIMA"),
    ("tab-rolling",        "Técnica Rolling"),
    ("tab-conclusiones",   "Conclusiones"),
]

TAB_LAYOUT_MAP = {
    "tab-introduccion":   introduccion.layout,
    "tab-contexto":       contexto.layout,
    "tab-problema":       problema.layout,
    "tab-objetivos":      objetivos.layout,
    "tab-marco":          marco_teorico.layout,
    "tab-metodologia":    metodologia.layout,
    "tab-resultados":     resultados.layout,
    "tab-prediccion":     prediccion.layout,
    "tab-arima-modelo":   arima_modelo.layout,
    "tab-arima-residuos": arima_residuos.layout,
    "tab-rolling":        rolling.layout,
    "tab-conclusiones":   conclusiones.layout,
}

app.layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand(
                "Tasas de Interés de Colocación · Banco de la República de Colombia",
                className="fw-bold",
                style={"color": "#F4EED8", "font-family": "Jost, sans-serif",
                       "font-size": "0.95rem", "letter-spacing": "0.3px"},
            ),
            dbc.Badge("1998 – 2025", color="secondary", text_color="light",
                      className="ms-auto small"),
        ], fluid=True),
        color="#0A0A0C", dark=True, className="mb-0 py-2 shadow-sm",
    ),
    dbc.Container([
        dcc.Tabs(
            id="main-tabs",
            value="tab-introduccion",
            children=[
                dcc.Tab(label=label, value=tab_id,
                        className="custom-tab",
                        selected_className="custom-tab--selected")
                for tab_id, label in TABS
            ],
            className="mt-3 mb-0",
        ),
        html.Div(id="tab-content", className="mt-0"),
    ], fluid=True,
       style={"min-height": "100vh", "background": "#141418", "padding-bottom": "40px"}),
], style={"font-family": "Jost, sans-serif", "background": "#0F0F12"})


@app.callback(Output("tab-content", "children"), Input("main-tabs", "value"))
def render_tab(tab_value):
    fn = TAB_LAYOUT_MAP.get(tab_value)
    if fn:
        return fn()
    return html.Div(dbc.Alert(f"Pestaña no encontrada.", color="warning"), className="mt-3")


if __name__ == "__main__":
    app.run(debug=True, port=8050, host="0.0.0.0")
