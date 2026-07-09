
import pandas as pd
import numpy as np
from scipy import stats

class PrecursorDetector:
    """
    Detector de precursores sismicos mediante analisis de deformacion vertical GNSS.

    Parametros
    ----------
    window_size : int, default=30
        Tamano de la ventana deslizante en dias.
    step : int, default=5
        Paso entre ventanas en dias.
    significance : float, default=0.05
        Umbral de significancia para la prueba de Mann-Kendall.
    """

    def __init__(self, window_size=30, step=5, significance=0.05):
        self.window_size = window_size
        self.step = step
        self.significance = significance
        self.data = None
        self.results = None

    def load_data(self, filepath, date_col='fecha', height_col='height'):
        """
        Carga un archivo .tenv3 del Nevada Geodetic Laboratory.

        Parametros
        ----------
        filepath : str
            Ruta al archivo .tenv3.
        date_col : str, default='fecha'
            Nombre de la columna de fechas.
        height_col : str, default='height'
            Nombre de la columna de altura.

        Returns
        -------
        self : PrecursorDetector
        """
        df = pd.read_csv(filepath, sep='\s+', header=0, comment=None)
        # Convertir fecha si es necesario (formato YYMMMDD)
        if 'YYMMMDD' in df.columns:
            df[date_col] = self._convert_yyyymmdd(df['YYMMMDD'])
        else:
            df[date_col] = pd.to_datetime(df[date_col])
        df[height_col] = df['__height(m)']
        df = df.dropna(subset=[date_col, height_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        self.data = df
        return self

    def _convert_yyyymmdd(self, series):
        """Convierte formato YYMMMDD a datetime."""
        meses = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6,
                 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
        def conv(fecha_str):
            if len(fecha_str) != 7:
                return pd.NaT
            anio = int(fecha_str[0:2])
            if anio >= 90:
                anio += 1900
            else:
                anio += 2000
            mes = meses.get(fecha_str[2:5].upper(), 1)
            dia = int(fecha_str[5:7])
            try:
                return pd.Timestamp(anio, mes, dia)
            except:
                return pd.NaT
        return series.apply(conv)

    def detect(self, start_date, end_date):
        """
        Ejecuta el algoritmo de deteccion en el periodo especificado.

        Parametros
        ----------
        start_date : str o datetime
            Fecha de inicio del periodo de analisis.
        end_date : str o datetime
            Fecha de fin del periodo de analisis.

        Returns
        -------
        dict
            Diccionario con los resultados:
            - p_value : float
            - tau : float
            - trend_direction : str ('creciente' o 'decreciente')
            - alert_level : str ('ALERTA' o 'NORMAL')
            - n_windows : int
            - windows : list
            - dates : list
        """
        if self.data is None:
            raise ValueError("No se han cargado datos. Use load_data() primero.")

        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)

        # Filtrar periodo
        mask = (self.data['fecha'] >= start) & (self.data['fecha'] <= end)
        periodo = self.data.loc[mask].copy()

        if len(periodo) < self.window_size:
            raise ValueError("El periodo es mas corto que el tamano de ventana.")

        # Datos previos para la tendencia base
        df_prev = self.data[self.data['fecha'] < start].copy()
        if len(df_prev) < 30:
            raise ValueError("Se necesitan al menos 30 dias de datos previos.")

        # Tendencia base (regresion lineal)
        df_prev['dias'] = (df_prev['fecha'] - df_prev['fecha'].min()).dt.days
        coef = np.polyfit(df_prev['dias'], df_prev['height'], 1)
        tendencia = np.poly1d(coef)

        # Calcular anomalias
        periodo['dias'] = (periodo['fecha'] - df_prev['fecha'].min()).dt.days
        periodo['residuo'] = periodo['height'] - tendencia(periodo['dias'])

        # Ventanas deslizantes
        ventanas = []
        fechas = []
        for i in range(0, len(periodo) - self.window_size + 1, self.step):
            ventana = periodo.iloc[i:i+self.window_size]
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
            raise ValueError("No hay suficientes ventanas para el analisis.")

        # Prueba de Mann-Kendall sobre las pendientes
        dias = [(f - start).days for f in fechas]
        tau, p_valor = stats.kendalltau(dias, ventanas)

        direccion = 'creciente' if tau > 0 else 'decreciente'
        alerta = 'ALERTA' if p_valor < self.significance else 'NORMAL'

        self.results = {
            'p_value': p_valor,
            'tau': tau,
            'trend_direction': direccion,
            'alert_level': alerta,
            'n_windows': len(ventanas),
            'windows': ventanas,
            'dates': fechas,
            'start_date': start,
            'end_date': end
        }

        return self.results

    def get_summary(self):
        """Devuelve un resumen en texto de los resultados."""
        if self.results is None:
            return "No hay resultados. Ejecute detect() primero."

        r = self.results
        return (
            f"Resumen de deteccion\n"
            f"Periodo: {r['start_date'].date()} a {r['end_date'].date()}\n"
            f"Ventanas: {r['n_windows']}\n"
            f"Mann-Kendall tau: {r['tau']:.4f}\n"
            f"P-valor: {r['p_value']:.6f}\n"
            f"Direccion: {r['trend_direction']}\n"
            f"Nivel de alerta: {r['alert_level']}"
        )