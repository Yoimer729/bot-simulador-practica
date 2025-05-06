# simulador_bot_trading.py

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Configuración general
SIMULAR = True  # Modo práctica
CAPITAL_INICIAL = 200000  # En COP
APORTE_MENSUAL = 200000
CAPITAL = CAPITAL_INICIAL
COMISION_PORCENTAJE = 0.002  # 0.2% por trade
HISTORIAL = []

# Configuración de estrategia
PAIR = "BTC-USDT"
INTERVAL = "5m"
LIMITE = 200
TAKE_PROFIT = 0.03  # 3%
STOP_LOSS = -0.015  # -1.5%

# Obtiene velas históricas (simuladas)
def obtener_datos():
    url = f"https://api.kucoin.com/api/v1/market/candles?type={INTERVAL}&symbol={PAIR}&limit={LIMITE}"
    response = requests.get(url)
    respuesta = response.json()
    datos = respuesta.get('data') or respuesta.get('datos') or respuesta

    df = pd.DataFrame(datos, columns=["timestamp", "open", "close", "high", "low", "volume", "turnover"])
    df = df.iloc[::-1].copy()
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    return df

# Indicadores técnicos
def calcular_ema(df, periodo):
    return df['close'].ewm(span=periodo, adjust=False).mean()

def calcular_rsi(df, periodo=14):
    delta = df['close'].diff()
    ganancia = delta.clip(lower=0)
    perdida = -1 * delta.clip(upper=0)
    avg_ganancia = ganancia.rolling(window=periodo).mean()
    avg_perdida = perdida.rolling(window=periodo).mean()
    rs = avg_ganancia / avg_perdida
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Simular operación
def simular_operacion(precio_entrada):
    global CAPITAL
    monto_operacion = CAPITAL * 0.3
    cantidad = monto_operacion / precio_entrada
    precio_salida_tp = precio_entrada * (1 + TAKE_PROFIT)
    precio_salida_sl = precio_entrada * (1 + STOP_LOSS)

    ganancia_tp = (precio_salida_tp - precio_entrada) * cantidad
    perdida_sl = (precio_salida_sl - precio_entrada) * cantidad

    comision = monto_operacion * COMISION_PORCENTAJE * 2

    resultado = {
        "entrada": precio_entrada,
        "salida_tp": precio_salida_tp,
        "salida_sl": precio_salida_sl,
        "ganancia": round(ganancia_tp - comision, 2),
        "perdida": round(perdida_sl - comision, 2),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return resultado

# Evaluar condiciones y simular entrada
def evaluar_estrategia(df):
    global CAPITAL
    df['ema9'] = calcular_ema(df, 9)
    df['ema21'] = calcular_ema(df, 21)
    df['ema200'] = calcular_ema(df, 200)
    df['rsi'] = calcular_rsi(df)

    ultima = df.iloc[-1]
    anterior = df.iloc[-2]

    # Condiciones para entrada
    if (
        anterior['ema9'] < anterior['ema21'] and
        ultima['ema9'] > ultima['ema21'] and
        ultima['close'] > ultima['ema200'] and
        45 <= ultima['rsi'] <= 70
    ):
        operacion = simular_operacion(ultima['close'])
        CAPITAL += operacion['ganancia']
        HISTORIAL.append({"tipo": "compra", **operacion})
        print(f"\n✅ COMPRA SIMULADA: {operacion}\nCapital actual: {round(CAPITAL, 2)} COP")

# Bucle principal
def ejecutar_simulacion():
    print("\n🧠 Iniciando simulador de bot de trading... (Modo Práctica)")
    for _ in range(3):  # Ejecutamos 3 simulaciones seguidas por ejemplo
        df = obtener_datos()
        evaluar_estrategia(df)
        time.sleep(5)  # Esperar 5 segundos entre cada evaluación

    print("\n📊 Historial de operaciones simuladas:")
    for op in HISTORIAL:
        print(op)

if __name__ == "__main__":
    ejecutar_simulacion()
