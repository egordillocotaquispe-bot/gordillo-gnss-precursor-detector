
import pandas as pd
import matplotlib.pyplot as plt

def load_tenv3(filepath):
    """
    Carga un archivo .tenv3 y devuelve un DataFrame con columnas 'fecha' y 'height'.

    Parametros
    ----------
    filepath : str
        Ruta al archivo .tenv3.

    Returns
    -------
    pd.DataFrame
        DataFrame con columnas 'fecha' (datetime) y 'height' (float).
    """
    meses = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6,
             'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}

    def convertir_fecha(fecha_str):
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

    df = pd.read_csv(filepath, sep='\s+', header=0, comment=None)
    if 'YYMMMDD' in df.columns:
        df['fecha'] = df['YYMMMDD'].apply(convertir_fecha)
    else:
        df['fecha'] = pd.to_datetime(df['fecha'])
    df['height'] = df['__height(m)']
    df = df.dropna(subset=['fecha', 'height'])
    df = df.sort_values('fecha').reset_index(drop=True)
    return df[['fecha', 'height']]

def plot_results(results, title=None, save_path=None):
    """
    Grafica la evolucion de las pendientes de anomalias.

    Parametros
    ----------
    results : dict
        Diccionario de resultados devuelto por PrecursorDetector.detect().
    title : str, optional
        Titulo del grafico.
    save_path : str, optional
        Ruta para guardar la figura (ej. 'grafico.png').
    """
    if results is None:
        raise ValueError("El diccionario de resultados no puede ser None.")

    fechas = results['dates']
    pendientes = results['windows']

    plt.figure(figsize=(14, 6))
    plt.plot(fechas, pendientes, 'o-', color='blue', linewidth=1.5, markersize=6)
    plt.axhline(y=0, color='black', linestyle=':', linewidth=1)
    plt.xlabel('Fecha de inicio de ventana')
    plt.ylabel('Pendiente de anomalias (mm/año)')
    if title:
        plt.title(title)
    else:
        plt.title('Evolucion de la pendiente de anomalias')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)

    plt.show()

def generar_resumen_csv(results, output_path='resultados.csv'):
    """
    Guarda los resultados en un archivo CSV.

    Parametros
    ----------
    results : dict
        Diccionario de resultados.
    output_path : str, default='resultados.csv'
        Ruta del archivo de salida.
    """
    if results is None:
        raise ValueError("El diccionario de resultados no puede ser None.")

    df = pd.DataFrame({
        'fecha': results['dates'],
        'pendiente_mm_anio': results['windows']
    })
    df.to_csv(output_path, index=False)