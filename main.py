from flask import Flask
import threading
import time
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

# --- Configuración del simulador ---
CAPITAL = 200000
USDT_POR_OPERACION = 20000
TASA_USDT = 4000
COMISION = 0.002
LIMITE = 100
historial = []
CSV_PATH = "resultados.csv"

# Si el CSV no existe, crear el archivo con encabezados
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=["Fecha", "Entrada", "Salida", "Resultado", "Ganancia_COP", "Capital_Actual"]).to_csv(CSV_PATH, index=False)

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
    cambio_pct = np.random.choice([0.03, -0.015], p=[0.6, 0.4])
    precio_salida = precio_entrada * (1 + cambio_pct)
    resultado = "GANANCIA" if cambio_pct > 0 else "PÉRDIDA"
    ganancia_neta = USDT_POR_OPERACION * cambio_pct * (1 - COMISION)
    return precio_salida, ganancia_neta, resultado

def bot_loop():
    global CAPITAL
    for i in range(100):  # número de operaciones
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
            
            # Guardar en CSV
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Entrada": round(precio_entrada, 2),
                "Salida": round(precio_salida, 2),
                "Resultado": resultado,
                "Ganancia_COP": round(ganancia_neta, 2),
                "Capital_Actual": round(CAPITAL, 2)
            }])
            nueva_fila.to_csv(CSV_PATH, mode='a', index=False, header=False)
        else:
            print(f"[{datetime.now()}] No hay señal válida.")
        time.sleep(5)

@app.route('/')
def home():
    total_op = len(historial)
    ganancia_total = sum([x["ganancia_cop"] for x in historial]) if historial else 0
    return f"✅ Bot de simulación activo<br>Capital actual: {CAPITAL:.2f} COP<br>Operaciones: {total_op}<br>Ganancia neta: {ganancia_total:.2f} COP"

def start_bot_background():
    thread = threading.Thread(target=bot_loop)
    thread.start()

start_bot_background()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
