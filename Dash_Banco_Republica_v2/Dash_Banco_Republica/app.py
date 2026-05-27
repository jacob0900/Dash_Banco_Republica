"""
app.py
Punto de entrada principal del dashboard.
Banco de la República de Colombia – Tasas de Interés de Colocación
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

from tabs import (
    introduccion,
    contexto,
    problema,
    objetivos,
    marco_teorico,
    metodologia,
    resultados,
    rolling,
    arima_modelo,
    arima_residuos,
    prediccion,
    conclusiones,
)

# ── Inicialización ────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Banco de la República – Tasas de Colocación",
)
server = app.server  # gunicorn usa este objeto


# ── Navegación ────────────────────────────────────────────────────────────────
TABS = [
    ("tab-introduccion",   "Introducción"),
    ("tab-contexto",       "Contexto"),
    ("tab-problema",       "Problema"),
    ("tab-objetivos",      "Objetivos"),
    ("tab-marco",          "Marco Teórico"),
    ("tab-metodologia",    "Metodología"),
    ("tab-resultados",     "Resultados EDA"),
    ("tab-arima-modelo",   "Modelo ARIMA"),
    ("tab-arima-residuos", "Residuos ARIMA"),
    ("tab-rolling",        "Rolling"),
    ("tab-prediccion",     "Predicción"),
    ("tab-conclusiones",   "Conclusiones"),
]

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            "Banco de la República · Tasas de Colocación",
            className="fw-bold",
            style={"color": "#F5C842", "font-size": "1rem"},
        ),
    ], fluid=True),
    color="#0F0F12",
    dark=True,
    sticky="top",
    style={"border-bottom": "2px solid #B8860B"},
)

tab_items = dbc.Nav(
    [
        dbc.NavItem(
            dbc.NavLink(
                label,
                id=tab_id,
                href="#",
                n_clicks=0,
                className="dash-tab-link",
                style={
                    "color": "#CEC5A8",
                    "font-size": "0.82rem",
                    "padding": "6px 10px",
                    "white-space": "nowrap",
                },
            )
        )
        for tab_id, label in TABS
    ],
    pills=True,
    className="flex-nowrap overflow-auto px-3 py-2",
    style={"background": "#141418", "border-bottom": "1px solid #2E2E38"},
)

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    [
        navbar,
        tab_items,
        dcc.Store(id="active-tab", data="tab-introduccion"),
        html.Div(id="page-content", style={"minHeight": "90vh"}),
    ],
    style={"background": "#0F0F12", "minHeight": "100vh"},
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
TAB_IDS = [t[0] for t in TABS]


@app.callback(
    Output("active-tab", "data"),
    [Input(tab_id, "n_clicks") for tab_id in TAB_IDS],
    prevent_initial_call=True,
)
def update_active_tab(*args):
    from dash import ctx
    if not ctx.triggered_id:
        return "tab-introduccion"
    return ctx.triggered_id


@app.callback(
    Output("page-content", "children"),
    Input("active-tab", "data"),
)
def render_content(tab):
    mapping = {
        "tab-introduccion":   introduccion.layout,
        "tab-contexto":       contexto.layout,
        "tab-problema":       problema.layout,
        "tab-objetivos":      objetivos.layout,
        "tab-marco":          marco_teorico.layout,
        "tab-metodologia":    metodologia.layout,
        "tab-resultados":     resultados.layout,
        "tab-arima-modelo":   arima_modelo.layout,
        "tab-arima-residuos": arima_residuos.layout,
        "tab-rolling":        rolling.layout,
        "tab-prediccion":     prediccion.layout,
        "tab-conclusiones":   conclusiones.layout,
    }
    fn = mapping.get(tab, introduccion.layout)
    return fn()


# ── Ejecución local ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
