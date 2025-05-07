# main.py (versión demo/simulación)
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Configuración
PAIR = "BTC-USDT"
INTERVAL = "5min"
LIMITE = 100
CAPITAL_INICIAL = 200000  # En COP
CAPITAL = CAPITAL_INICIAL
USDT_POR_OPERACION = 20000  # Simulación por operación en COP
TASA_USDT = 4000  # Simulación: tasa del dólar para convertir
COMISION = 0.002  # 0.2%
historial = []

# Función para simular velas
def obtener_velas_simuladas():
    precios = np.linspace(100, 110, LIMITE) + np.random.normal(0, 0.5, LIMITE)
    df = pd.DataFrame(precios, columns=["close"])
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    return df

def evaluar_entrada(df):
    c = df.iloc[-1]
    c_ant = df.iloc[-2]
    return (
        c["ema9"] > c["ema21"]
        and c_ant["ema9"] <= c_ant["ema21"]
        and c["close"] > c["ema9"]
    )

def simular_trade(precio_entrada):
    cambio_pct = np.random.choice([0.03, -0.015], p=[0.6, 0.4])  # 60% ganar
    precio_salida = precio_entrada * (1 + cambio_pct)
    resultado = "GANANCIA" if cambio_pct > 0 else "PÉRDIDA"
    ganancia_neta = USDT_POR_OPERACION * cambio_pct * (1 - COMISION)
    return precio_salida, ganancia_neta, resultado

# Bucle principal (simulación por 20 operaciones)
for i in range(20):
    df = obtener_velas_simuladas()
    if evaluar_entrada(df):
        precio_entrada = df["close"].iloc[-1]
        precio_salida, ganancia_neta, resultado = simular_trade(precio_entrada)
        CAPITAL += ganancia_neta
        historial.append({
            "n°": i+1,
            "entrada": round(precio_entrada, 2),
            "salida": round(precio_salida, 2),
            "resultado": resultado,
            "ganancia_cop": round(ganancia_neta, 2),
            "capital_actual": round(CAPITAL, 2)
        })
        print(f"[{datetime.now()}] {resultado}: entrada {precio_entrada:.2f} → salida {precio_salida:.2f} | Ganancia: {ganancia_neta:.2f} | Capital: {CAPITAL:.2f}")
    else:
        print(f"[{datetime.now()}] No hay señal válida.")
    time.sleep(1)

# Mostrar resumen
import pandas as pd
df_hist = pd.DataFrame(historial)
df_hist.to_csv("simulacion_resultados.csv", index=False)
print("\nSimulación finalizada. Resultado guardado en 'simulacion_resultados.csv'")
