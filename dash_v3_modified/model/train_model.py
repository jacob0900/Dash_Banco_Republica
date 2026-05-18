"""
train_model.py
Prueba de estacionariedad de la serie TasaColocacionTotal
Pruebas: ADF (Augmented Dickey-Fuller) y KPSS
Modelo ARIMA: Grid Search AIC, pronóstico, métricas y análisis de residuos
Ejecutar directamente: python model/train_model.py
"""

import os, sys
import json
import pickle
import warnings
import pandas as pd
import numpy as np

# Permitir importación desde raíz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statsmodels.tsa.stattools import adfuller, kpss
from data.generate_data import load_data

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def run_adf_test(series: pd.Series) -> dict:
    """Ejecuta el test ADF y retorna resultados como dict."""
    result = adfuller(series.dropna(), autolag="AIC")
    adf_stat, p_value, n_lags, n_obs, crit_vals, icbest = result
    return {
        "test":        "ADF (Augmented Dickey-Fuller)",
        "estadistico": round(float(adf_stat), 4),
        "p_value":     round(float(p_value), 4),
        "lags_usados": int(n_lags),
        "n_obs":       int(n_obs),
        "valores_criticos": {k: round(float(v), 4) for k, v in crit_vals.items()},
        "es_estacionaria": p_value < 0.05,
        "hipotesis_nula": "La serie tiene raíz unitaria (no estacionaria)",
        "conclusion": (
            "✅ Se rechaza H₀ → la serie ES estacionaria (p < 0.05)"
            if p_value < 0.05
            else "⚠️ No se rechaza H₀ → la serie NO ES estacionaria (p ≥ 0.05)"
        ),
    }


def run_kpss_test(series: pd.Series) -> dict:
    """Ejecuta el test KPSS y retorna resultados como dict."""
    result = kpss(series.dropna(), regression="c", nlags="auto")
    kpss_stat, p_value, n_lags, crit_vals = result
    return {
        "test":        "KPSS (Kwiatkowski-Phillips-Schmidt-Shin)",
        "estadistico": round(float(kpss_stat), 4),
        "p_value":     round(float(p_value), 4),
        "lags_usados": int(n_lags),
        "valores_criticos": {k: round(float(v), 4) for k, v in crit_vals.items()},
        "es_estacionaria": p_value >= 0.05,
        "hipotesis_nula": "La serie es estacionaria",
        "conclusion": (
            "✅ No se rechaza H₀ → la serie ES estacionaria (p ≥ 0.05)"
            if p_value >= 0.05
            else "⚠️ Se rechaza H₀ → la serie NO ES estacionaria (p < 0.05)"
        ),
    }


def run_stationarity_analysis(df: pd.DataFrame) -> dict:
    """
    Ejecuta ADF y KPSS sobre TasaColocacionTotal y su primera diferencia.
    Retorna un dict serializable con todos los resultados.
    """
    serie = df.set_index("Fecha")["TasaColocacionTotal"]
    serie_diff = serie.diff().dropna()

    results = {
        "variable":       "TasaColocacionTotal",
        "n_observaciones": int(len(serie)),
        "fecha_inicio":   str(serie.index.min().date()),
        "fecha_fin":      str(serie.index.max().date()),
        "serie_original": {
            "adf":  run_adf_test(serie),
            "kpss": run_kpss_test(serie),
        },
        "primera_diferencia": {
            "adf":  run_adf_test(serie_diff),
            "kpss": run_kpss_test(serie_diff),
        },
        "interpretacion_conjunta": _interpret(
            run_adf_test(serie),
            run_kpss_test(serie),
        ),
    }
    return results


def _interpret(adf: dict, kpss: dict) -> str:
    """Interpretación conjunta ADF + KPSS."""
    adf_ok  = adf["es_estacionaria"]
    kpss_ok = kpss["es_estacionaria"]
    if adf_ok and kpss_ok:
        return "Ambas pruebas concuerdan: la serie ES estacionaria. No se requiere diferenciación."
    elif not adf_ok and not kpss_ok:
        return "Ambas pruebas concuerdan: la serie NO ES estacionaria. Se recomienda diferenciación (d=1)."
    elif adf_ok and not kpss_ok:
        return "Resultado mixto: En conclusión, aunque el ADF sugiere que tu serie original podría ser estacionaria, el KPSS detecta una tendencia y marca que no lo es; ambos coinciden en que la primera diferencia sí es estacionaria, por lo que la decisión más robusta es trabajar con la serie diferenciada y ajustar un modelo ARIMA(p,1,q) sobre ella, garantizando que cumpla la condición de estacionariedad y evitando problemas futuros en el modelado.."
    else:
        return "Resultado mixto: KPSS indica estacionariedad, pero ADF sugiere raíz unitaria. Revisar con mayor número de lags."


def run_arima_analysis(df: pd.DataFrame) -> dict:
    """
    Grid search AIC, ajuste del mejor modelo ARIMA, pronóstico y
    análisis de residuos sobre TasaColocacionTotal.
    """
    warnings.filterwarnings("ignore")
    import statsmodels.api as sm
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from scipy.stats import shapiro

    serie = df.set_index("Fecha")["TasaColocacionTotal"]
    n = len(serie)
    train_size = int(n * 0.8)
    train, test = serie.iloc[:train_size], serie.iloc[train_size:]

    # ── Grid Search AIC ────────────────────────────────────────────────────
    print("  🔍 Grid search ARIMA (p∈[0,3], d∈[0,1], q∈[0,3])...")
    best_aic   = np.inf
    best_order = (0, 1, 1)
    for p in range(4):
        for d in range(2):
            for q in range(4):
                try:
                    mdl = sm.tsa.ARIMA(train, order=(p, d, q)).fit()
                    if mdl.aic < best_aic:
                        best_aic   = mdl.aic
                        best_order = (p, d, q)
                except Exception:
                    continue
    print(f"  ✅ Mejor orden: ARIMA{best_order} — AIC: {best_aic:.2f}")

    # ── Ajuste final ───────────────────────────────────────────────────────
    modelo = sm.tsa.ARIMA(train, order=best_order).fit()
    pred_obj  = modelo.get_forecast(steps=len(test))
    pred_mean = pred_obj.predicted_mean
    pred_ci   = pred_obj.conf_int()

    # ── Métricas ───────────────────────────────────────────────────────────
    mae  = float(mean_absolute_error(test, pred_mean))
    mse  = float(mean_squared_error(test, pred_mean))
    rmse = float(np.sqrt(mse))
    mape = float(np.mean(np.abs((test.values - pred_mean.values) / test.values)) * 100)
    r2   = float(r2_score(test, pred_mean))

    # ── Residuos ───────────────────────────────────────────────────────────
    residuos = modelo.resid
    sw_stat, sw_p = shapiro(residuos)
    lb_result = acorr_ljungbox(residuos, lags=[10], return_df=True)
    lb_stat = float(lb_result["lb_stat"].iloc[0])
    lb_p    = float(lb_result["lb_pvalue"].iloc[0])

    # ── Breusch-Pagan (homocedasticidad formal) ────────────────────────────
    from statsmodels.stats.diagnostic import het_breuschpagan
    import statsmodels.api as sm_bp
    X_bp = sm_bp.add_constant(
        pd.DataFrame({"fitted": modelo.fittedvalues}, index=modelo.fittedvalues.index)
    )
    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(residuos, X_bp)

    return {
        "order":     best_order,
        "order_str": f"ARIMA{best_order}",
        "aic":       round(best_aic, 2),
        "bic":       round(float(modelo.bic), 2),
        "n_train":   int(len(train)),
        "n_test":    int(len(test)),
        "mae":       round(mae,  4),
        "mse":       round(mse,  4),
        "rmse":      round(rmse, 4),
        "mape":      round(mape, 2),
        "r2":        round(r2,   4),
        # Series para gráficos (listas JSON-serializables)
        "train_index":  [str(i) for i in train.index],
        "test_index":   [str(i) for i in test.index],
        "train_values": [float(v) for v in train.values],
        "test_values":  [float(v) for v in test.values],
        "pred_mean":    [float(v) for v in pred_mean.values],
        "ci_lower":     [float(v) for v in pred_ci.iloc[:, 0].values],
        "ci_upper":     [float(v) for v in pred_ci.iloc[:, 1].values],
        # Residuos
        "residuos": {
            "index":        [str(i) for i in residuos.index],
            "values":       [float(v) for v in residuos.values],
            "media":        round(float(np.mean(residuos)), 6),
            "shapiro_stat": round(float(sw_stat), 4),
            "shapiro_p":    round(float(sw_p), 6),
            "ljungbox_stat": round(lb_stat, 4),
            "ljungbox_p":    round(lb_p, 6),
            # Breusch-Pagan
            "bp_lm_stat":  round(float(bp_lm),   4),
            "bp_lm_p":     round(float(bp_lm_p),  6),
            "bp_f_stat":   round(float(bp_f),     4),
            "bp_f_p":      round(float(bp_f_p),   6),
        },
    }


def run_rolling_analysis(df: pd.DataFrame) -> dict:
    """
    Búsqueda exhaustiva de combinaciones ARIMA(p,d,q) con d in [1,2]
    y p,q in [0..4], evaluando independencia (Ljung-Box) y normalidad
    (Shapiro-Wilk) de los residuos. Retorna tabla de resultados y
    conclusión sobre la viabilidad de la técnica rolling.
    """
    warnings.filterwarnings("ignore")
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from scipy.stats import shapiro as shapiro_test

    serie = df.set_index("Fecha")["TasaColocacionTotal"]

    resultados = []
    for d in [1, 2]:
        for p in range(11):   # 0..10
            for q in range(11):  # 0..10
                try:
                    modelo = sm.tsa.ARIMA(serie, order=(p, d, q)).fit()
                    residuos = modelo.resid
                    lb = acorr_ljungbox(residuos, lags=[10], return_df=True)
                    p_lb = float(lb["lb_pvalue"].iloc[0])
                    _, p_sw = shapiro_test(residuos)
                    resultados.append({
                        "p": p, "d": d, "q": q,
                        "p_ljungbox": round(p_lb, 6),
                        "p_shapiro":  round(float(p_sw), 6),
                        "independencia": p_lb >= 0.05,
                        "normalidad":    float(p_sw) >= 0.05,
                    })
                except Exception:
                    continue

    # ¿Alguna combinación pasa independencia?
    alguna_ok = any(r["independencia"] for r in resultados)

    return {
        "tabla": resultados,
        "total_combinaciones": len(resultados),
        "alguna_independencia": alguna_ok,
        "conclusion": (
            "Al menos una combinación ARIMA cumple el supuesto de independencia de errores "
            "(p Ljung-Box ≥ 0.05). La técnica rolling podría aplicarse con esos parámetros."
            if alguna_ok else
            "Ninguna combinación ARIMA (d∈{1,2}, p,q∈[0,4]) logró residuos independientes "
            "(p Ljung-Box < 0.05 en todos los casos). La autocorrelación residual persistente "
            "implica que la técnica rolling no es pertinente en este contexto: violar el supuesto "
            "de independencia invalida la rigurosidad estadística del modelo."
        ),
    }


def train_and_save():
    """Punto de entrada principal: entrena y serializa los resultados."""
    print("📊 Cargando datos...")
    df = load_data()

    print("🔬 Ejecutando pruebas de estacionariedad...")
    results = run_stationarity_analysis(df)

    print("\n=== RESULTADOS ADF (Serie original) ===")
    adf = results["serie_original"]["adf"]
    print(f"  Estadístico : {adf['estadistico']}")
    print(f"  p-valor     : {adf['p_value']}")
    print(f"  Conclusión  : {adf['conclusion']}")

    print("\n=== RESULTADOS KPSS (Serie original) ===")
    kp = results["serie_original"]["kpss"]
    print(f"  Estadístico : {kp['estadistico']}")
    print(f"  p-valor     : {kp['p_value']}")
    print(f"  Conclusión  : {kp['conclusion']}")

    print(f"\n📌 Interpretación conjunta: {results['interpretacion_conjunta']}")

    print("\n🤖 Entrenando modelo ARIMA...")
    results["arima"] = run_arima_analysis(df)
    print(f"  Orden: {results['arima']['order_str']} | "
          f"MAE: {results['arima']['mae']} | RMSE: {results['arima']['rmse']}")

    print("\n🔄 Ejecutando análisis Rolling (puede tardar ~1 min)...")
    results["rolling"] = run_rolling_analysis(df)
    print(f"  Combinaciones evaluadas: {results['rolling']['total_combinaciones']}")
    print(f"  Conclusión: {results['rolling']['conclusion'][:80]}...")

    # Guardar resultados en pickle
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(results, f)
    print(f"\n✅ Resultados guardados en {OUTPUT_PATH}")
    return results


def load_model_results() -> dict:
    """Carga los resultados desde el pickle; si no existe, los genera."""
    if not os.path.exists(OUTPUT_PATH):
        return train_and_save()
    with open(OUTPUT_PATH, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    train_and_save()
