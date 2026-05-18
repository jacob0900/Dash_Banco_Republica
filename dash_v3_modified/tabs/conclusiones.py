"""
tabs/conclusiones.py
Pestaña – Conclusiones del análisis de Tasas de Interés de Colocación.
"""

from tabs.svg_icons import svg_icon
from dash import html
import dash_bootstrap_components as dbc


CONCLUSIONES = [
    ("C1", "Comportamiento Histórico de la Serie",
     """La Tasa de Colocación Total exhibe una tendencia estructuralmente decreciente desde los niveles
     máximos registrados durante la crisis financiera colombiana de 1998–1999, cuando superó el 53%.
     A partir de 2002 se estabilizó progresivamente en rangos del 10–20%, con interrupciones asociadas
     a choques externos como la crisis financiera global de 2008 y la pandemia de COVID-19 en 2020,
     que llevaron las tasas a mínimos históricos, seguida por un ciclo agresivo de alzas en 2022–2023.""",
     "#e8edf7"),
    ("C2", "Correlación entre Modalidades de Crédito",
     """Las pruebas de correlación de Spearman sobre la primera diferencia de las series revelan que,
     una vez eliminada la tendencia común, la mayoría de los pares de variables no presentan asociación
     estadísticamente significativa (p > 0.05), a excepción del par Tesorería × Ordinarios (r = −0.175,
     p = 0.0023). Este resultado indica que los cambios mensuales en cada modalidad de crédito operan
     de forma relativamente independiente, lo cual tiene implicaciones relevantes para la modelación
     multivariada y la gestión del riesgo sistémico.""",
     "#e8f4ee"),
    ("C3", "Estacionariedad y Modelado",
     """Las pruebas ADF y KPSS aplicadas sobre la Tasa de Colocación Total arrojan un resultado mixto:
     el ADF sugiere estacionariedad en la serie original, mientras que el KPSS detecta la presencia de
     una tendencia determinística. Ambas pruebas coinciden en que la primera diferencia es estacionaria,
     lo que indica que la serie es integrada de orden uno I(1). La decisión metodológicamente más robusta
     es trabajar con la serie diferenciada y ajustar un modelo ARIMA(p, 1, q), garantizando el
     cumplimiento de los supuestos de estacionariedad.""",
     "#fef9e7"),
    ("C4", "Distribución y Asimetría",
     """Todas las variables analizadas presentan distribuciones asimétricas positivas, con medias
     superiores a las medianas. Este comportamiento es consecuencia directa de los valores extremadamente
     altos registrados durante la crisis de finales del siglo XX, los cuales elevan la media por encima
     del percentil 50. La desviación estándar de la Tasa Total (6.66 pp) refleja una variabilidad
     moderada a lo largo del período, con un rango efectivo que oscila entre 8.16% y 53.54%.""",
     "#fdf2f2"),
]

RECOMENDACIONES = [
    ("Para Investigadores",
     ["Incorporar variables macroeconómicas exógenas como inflación y PIB (modelos ARIMAX)",
      "Explorar modelos SARIMA para capturar posibles patrones estacionales en la serie",
      "Aplicar pruebas de cambio estructural (Chow, Bai-Perron) para identificar quiebres"],
     "text-primary"),
    ("Para el Sector Financiero",
     ["Utilizar las proyecciones de tasas como insumo para la planificación de portafolios de crédito",
      "Integrar el dashboard con datos en tiempo real del portal estadístico del Banco de la República",
      "Desarrollar alertas tempranas ante cambios de régimen en la política monetaria"],
     "text-success"),
    ("Para Política Pública",
     ["Monitorear la transmisión diferencial de la política monetaria por segmento de crédito",
      "Diseñar indicadores de seguimiento de ciclos crediticios con frecuencia mensual",
      "Evaluar el impacto de decisiones de tasa de referencia sobre cada modalidad de crédito"],
     "text-warning"),
]


def layout():
    return dbc.Container([

        # Título
        dbc.Row(dbc.Col(html.H3("Conclusiones",
            className="fw-bold pt-3 mb-1", style={"color": "#F5C842"}), width=12)),
        dbc.Row(dbc.Col(html.P(
            "Hallazgos principales del análisis de tasas de interés de colocación del Banco de la República",
            className="text-muted mb-4", style={"font-size": "1rem"}), width=12)),

        # Banner
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.P("""El presente trabajo realizó un análisis exploratorio completo de las series históricas
                   de tasas de interés de colocación del sistema financiero colombiano (1998–2025), combinando
                   estadística descriptiva, análisis de correlación mediante el método de Spearman y pruebas
                   formales de estacionariedad (ADF y KPSS). A continuación se presentan los hallazgos
                   más relevantes y las recomendaciones derivadas del análisis.""",
                   className="mb-0",
                   style={"color": "#E8D5A3", "font-size": "1rem", "line-height": "1.85"}),
        ]), className="shadow-sm border-0 mb-4",
           style={"background": "#1C1C22", "border-radius": "12px",
                  "border-left": "4px solid #1a1a2e"}), width=12)),

        # Conclusiones
        dbc.Row(dbc.Col(html.H5("Conclusiones Principales",
            className="fw-semibold mb-3", style={"color": "#E8D5A3", "font-size": "1.1rem"}), width=12)),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(codigo, className="fw-bold mb-2 px-2 py-1 rounded-pill d-inline-block small",
                         style={"background": "#D4AF37", "color": "#E8D5A3"}),
                html.H6(titulo, className="fw-bold mb-2 mt-1",
                        style={"color": "#E8D5A3", "font-size": "0.95rem"}),
                html.P(desc, className="mb-0",
                       style={"color": "#E8D5A3", "font-size": "0.95rem", "line-height": "1.8"}),
            ]), className="shadow-sm border-0 h-100",
               style={"background": "#1C1C22", "border-radius": "12px"}),
            xs=12, md=6, className="mb-3")
            for codigo, titulo, desc, bg in CONCLUSIONES
        ]),

        # Recomendaciones
        dbc.Row(dbc.Col(html.H5("Recomendaciones",
            className="fw-semibold mb-3 mt-2", style={"color": "#E8D5A3", "font-size": "1.1rem"}), width=12)),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(titulo, className=f"fw-bold {color} mb-2",
                            style={"font-size": "0.95rem"}),
                    html.Ul([
                        html.Li(item, style={"color": "#E8D5A3", "font-size": "0.95rem",
                                             "line-height": "1.8", "margin-bottom": "4px"})
                        for item in items
                    ], className="ps-3"),
                ], md=4)
                for titulo, items, color in RECOMENDACIONES
            ])
        ]), className="shadow-sm border-0 mb-4",
           style={"background": "#1C1C22", "border-radius": "12px"}), width=12)),

        # Líneas futuras
        dbc.Row(dbc.Col(html.H5("Líneas Futuras de Investigación",
            className="fw-semibold mb-3", style={"color": "#E8D5A3", "font-size": "1.1rem"}), width=12)),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(
            html.Div([
                html.Span(label, className="badge me-2 mb-2 px-3 py-2",
                          style={"background": "#1C1C22", "color": color, "font-size": "0.88rem",
                                 "border-radius": "20px", "font-weight": "500"})
                for label, bg, color in [
                    ("Modelo ARIMA completo",           "#1a1a2e", "white"),
                    ("Redes Neuronales LSTM",            "#2c5f8a", "white"),
                    ("Modelos VAR Multivariados",        "#3d6b4f", "white"),
                    ("SARIMA con estacionalidad",        "#7a4419", "white"),
                    ("Modelos GARCH (volatilidad)",      "#5c3472", "white"),
                    ("Dashboard en tiempo real",         "#1a5276", "white"),
                    ("Análisis de cointegración",        "#4a4a6a", "white"),
                    ("Modelos de cambio de régimen",     "#6b2d2d", "white"),
                ]
            ])
        ), className="shadow-sm border-0 mb-4",
           style={"background": "#1C1C22", "border-radius": "12px"}), width=12)),

        # Fuente
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(
            html.P("Fuente de datos: Banco de la República de Colombia – Sistema estadístico de tasas de "
                   "interés de colocación. Series históricas mensuales disponibles en banrep.gov.co",
                   className="text-muted text-center mb-0",
                   style={"font-size": "0.85rem"})
        ), className="border-0", style={"background": "#1C1C22", "border-radius": "10px"}), width=12)),

    ], fluid=True, className="px-3 py-3")
