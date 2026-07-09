
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detector import PrecursorDetector
from src.utils import plot_results

print("=" * 70)
print("VALIDACION: Terremoto de Iquique 2014 (Mw 8.2)")
print("Estaciones: PSGA, AEDA, ATJN")
print("=" * 70)

estaciones = ['PSGA', 'AEDA', 'ATJN']
resultados_estaciones = {}

for codigo in estaciones:
    print(f"\n--- Procesando {codigo} ---")
    try:
        detector = PrecursorDetector(window_size=30, step=5, significance=0.05)
        detector.load_data(f'{codigo}.tenv3')
        resultados = detector.detect(start_date='2013-10-01', end_date='2014-04-01')

        resultados_estaciones[codigo] = resultados

        print(f"P-valor: {resultados['p_value']:.6f}")
        print(f"Tau de Kendall: {resultados['tau']:.4f}")
        print(f"Direccion: {resultados['trend_direction']}")
        print(f"Alerta: {resultados['alert_level']}")
        print(f"Ventanas: {resultados['n_windows']}")

    except FileNotFoundError:
        print(f"Archivo {codigo}.tenv3 no encontrado. Saltando...")
    except Exception as e:
        print(f"Error con {codigo}: {e}")

# Resumen
print("\n" + "=" * 70)
print("RESUMEN DE VALIDACION - IQUIQUE 2014")
print("=" * 70)
for codigo, res in resultados_estaciones.items():
    print(f"{codigo}: p = {res['p_value']:.6f}, {res['alert_level']}")

# Graficar resultados de la primera estacion exitosa
if resultados_estaciones:
    primera = list(resultados_estaciones.keys())[0]
    print(f"\nGraficando resultados de {primera}...")
    plot_results(
        resultados_estaciones[primera],
        title=f'Iquique 2014 - {primera} - Evolucion de la pendiente de anomalias'
    )

print("\nValidacion completada.")