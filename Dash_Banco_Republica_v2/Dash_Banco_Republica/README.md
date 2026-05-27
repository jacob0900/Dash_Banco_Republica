# Dash – Banco de la República

Aplicación interactiva desarrollada en Python con Plotly Dash para visualizar y analizar las tasas de interés de colocación del Banco de la República de Colombia (series históricas mensuales 1998–2025).

## Estructura del proyecto

```
├── app.py                  # Punto de entrada principal
├── Procfile                # Comando de inicio para Render/Heroku
├── render.yaml             # Configuración de deploy en Render
├── requirements.txt        # Dependencias Python
├── runtime.txt             # Versión de Python
├── assets/
│   └── custom.css          # Estilos globales (tema Obsidian Gold)
├── data/
│   ├── File.xlsx           # Dataset fuente
│   └── generate_data.py    # Carga y limpieza de datos
├── model/
│   ├── model.pkl           # Modelo ARIMA pre-entrenado
│   └── train_model.py      # Entrenamiento y serialización del modelo
└── tabs/                   # Pestañas del dashboard
    ├── introduccion.py
    ├── contexto.py
    ├── problema.py
    ├── objetivos.py
    ├── marco_teorico.py
    ├── metodologia.py
    ├── resultados.py
    ├── rolling.py
    ├── arima_modelo.py
    ├── arima_residuos.py
    ├── prediccion.py
    └── conclusiones.py
```

## Ejecución local

```bash
# 1. Clonar el repositorio
git clone https://github.com/jacob0900/Dash_Banco_Republica.git
cd Dash_Banco_Republica

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la app
python app.py
```

Abrir en el navegador: http://127.0.0.1:8050

## Deploy en Render

1. Subir este repositorio a GitHub.
2. En [render.com](https://render.com), crear un nuevo **Web Service** conectado al repo.
3. Render detectará el `render.yaml` automáticamente y usará:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:server`
4. Deploy listo en ~3 minutos.
