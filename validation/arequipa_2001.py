
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detector import PrecursorDetector
from src.utils import plot_results

print("=" * 70)
print("VALIDACION: Terremoto de Arequipa 2001 (Mw 8.4)")
print("Estacion: AREQ")
print("=" * 70)

# Inicializar detector
detector = PrecursorDetector(window_size=30, step=5, significance=0.05)

# Cargar datos
detector.load_data('AREQ.tenv3')

# Ejecutar deteccion para el periodo previo al terremoto
resultados = detector.detect(start_date='2001-01-01', end_date='2001-06-22')

# Mostrar resultados
print("\nResultados:")
print(f"P-valor: {resultados['p_value']:.6f}")
print(f"Tau de Kendall: {resultados['tau']:.4f}")
print(f"Direccion de la tendencia: {resultados['trend_direction']}")
print(f"Nivel de alerta: {resultados['alert_level']}")
print(f"Numero de ventanas: {resultados['n_windows']}")

# Generar grafico
plot_results(resultados, title='Arequipa 2001 - Evolucion de la pendiente de anomalias')

print("\nValidacion completada.")