
import sys
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detector import PrecursorDetector

print("=" * 70)
print("SHUFFLE TEST - PRUEBA DE RUIDO BLANCO")
print("Validando que la señal de 2001 no es ruido aleatorio")
print("1000 permutaciones")
print("=" * 70)

# Configuracion
ARCHIVO = 'AREQ.tenv3'
START_DATE = '2001-01-01'
END_DATE = '2001-06-22'
N_SHUFFLES = 1000
WINDOW_SIZE = 30
STEP = 5
SIGNIFICANCE = 0.05

def calcular_pvalor_mannkendall(df, start_date, end_date, window_size, step):
    """
    Calcula el p-valor de Mann-Kendall para el periodo especificado.
    """
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    mask = (df['fecha'] >= start) & (df['fecha'] <= end)
    periodo = df.loc[mask].copy()

    if len(periodo) < window_size:
        return np.nan

    df_prev = df[df['fecha'] < start].copy()
    if len(df_prev) < 30:
        return np.nan

    df_prev['dias'] = (df_prev['fecha'] - df_prev['fecha'].min()).dt.days
    coef = np.polyfit(df_prev['dias'], df_prev['height'], 1)
    tendencia = np.poly1d(coef)

    periodo['dias'] = (periodo['fecha'] - df_prev['fecha'].min()).dt.days
    periodo['residuo'] = periodo['height'] - tendencia(periodo['dias'])

    ventanas = []
    fechas = []
    for i in range(0, len(periodo) - window_size + 1, step):
        ventana = periodo.iloc[i:i+window_size]
        if len(ventana) < 10:
            continue
        ventana['dias_local'] = (ventana['fecha'] - ventana['fecha'].min()).dt.days
        if len(ventana) < 2:
            continue
        coef_v = np.polyfit(ventana['dias_local'], ventana['residuo'], 1)
        pendiente_mm_anio = coef_v[0] * 365 * 1000
        ventanas.append(pendiente_mm_anio)
        fechas.append(ventana['fecha'].iloc[0])

    if len(ventanas) < 5:
        return np.nan

    dias = [(f - start).days for f in fechas]
    tau, p_valor = stats.kendalltau(dias, ventanas)
    return p_valor

# 1. Cargar datos originales
print("\nCargando datos originales...")
try:
    detector = PrecursorDetector(window_size=WINDOW_SIZE, step=STEP, significance=SIGNIFICANCE)
    detector.load_data(ARCHIVO)
    df_original = detector.data
    print("Datos cargados correctamente.")
except Exception as e:
    print(f"Error al cargar datos: {e}")
    exit()

# 2. Calcular p-valor real
print("\nCalculando p-valor real...")
p_real = calcular_pvalor_mannkendall(df_original, START_DATE, END_DATE, WINDOW_SIZE, STEP)
if np.isnan(p_real):
    print("Error al calcular p-valor real.")
    exit()
print(f"P-valor real: {p_real:.6f}")

# 3. Ejecutar shuffles
print(f"\nEjecutando {N_SHUFFLES} permutaciones...")
p_shuffles = []
for i in range(N_SHUFFLES):
    # Permutar aleatoriamente los valores de altura
    df_shuffle = df_original.copy()
    df_shuffle['height'] = np.random.permutation(df_shuffle['height'].values)

    p = calcular_pvalor_mannkendall(df_shuffle, START_DATE, END_DATE, WINDOW_SIZE, STEP)
    if not np.isnan(p):
        p_shuffles.append(p)

    if (i + 1) % 100 == 0:
        print(f"  {i+1}/{N_SHUFFLES} completados...")

# 4. Analisis estadistico
n_shuffles_validos = len(p_shuffles)
p_menores = sum(1 for p in p_shuffles if p <= p_real)
prob_casualidad = p_menores / n_shuffles_validos if n_shuffles_validos > 0 else 1.0

print("\n" + "=" * 70)
print("RESULTADOS DEL SHUFFLE TEST")
print("=" * 70)
print(f"Permutaciones validas: {n_shuffles_validos}")
print(f"Permutaciones con p-valor <= al real: {p_menores}")
print(f"Probabilidad de casualidad: {prob_casualidad * 100:.2f}%")

if prob_casualidad < 0.05:
    print("\nVALIDADO: La señal es real. La probabilidad de que sea ruido es menor al 5%.")
else:
    print("\nATENCION: La señal podria ser ruido. La probabilidad de casualidad es mayor al 5%.")

# 5. Grafico
plt.figure(figsize=(14, 6))
plt.hist(p_shuffles, bins=30, color='gray', alpha=0.7, label='P-valores del shuffle')
plt.axvline(p_real, color='red', linewidth=3, label=f'P-valor real 2001 ({p_real:.4f})')
plt.xlabel('P-valor de Mann-Kendall')
plt.ylabel('Frecuencia')
plt.title('Shuffle Test: comparacion del p-valor real contra distribucion de ruido')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('shuffle_test_resultado.png', dpi=150)
print("\nGrafico guardado como 'shuffle_test_resultado.png'")

print("\nShuffle test completado.")