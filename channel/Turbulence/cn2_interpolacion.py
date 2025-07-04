# -*- coding: utf-8 -*-
"""
Módulo para obtener una función de interpolación para la varianza de Rytov (sigma²),
basada en los datos de Cn² y los parámetros del sistema.

Este módulo reemplaza la interpolación de Cn² por una interpolación directa
de sigma², que es físicamente más coherente.
"""
import numpy as np
from scipy.interpolate import interp1d
# Importamos los datos necesarios desde tu archivo de datos.
# El 'as' renombra las variables para mayor claridad.
from .pasosCn2 import tandas, elev as elev_deg, cn2 as cn2_table

# La única función que este módulo ofrecerá a otros archivos será get_f_sigma2
__all__ = ['get_f_sigma2']

# Diccionario para cachear funciones ya calculadas y mejorar la eficiencia
_sigma2_cache = {}

def get_f_sigma2(loss_params):
    """
    Crea y devuelve una función que mapea el ángulo de elevación (en radianes)
    directamente a la varianza de Rytov (sigma²).

    Utiliza los datos de Cn² de la tanda especificada y los parámetros del
    sistema para pre-calcular una tabla de sigma².
    """
    # Si la turbulencia está desactivada, devuelve una función que no hace nada (sigma²=0)
    if not loss_params.get('turbulencia', False):
        return lambda *args, **kwargs: 0.0
        
    # Extraemos los parámetros de la configuración
    tanda_label = loss_params.get('tanda_label')
    wl = loss_params.get('wavelength')
    H_turb = loss_params.get('L') # Usamos L como la altura de la atmósfera turbulenta
    
    # Validamos que tenemos todo lo necesario
    if not all([tanda_label, wl, H_turb]):
        raise ValueError("loss_params debe contener 'tanda_label', 'wavelength' y 'L'.")
        
    # Usamos una clave para ver si ya hemos hecho este cálculo antes
    cache_key = (tanda_label, wl, H_turb)
    if cache_key in _sigma2_cache:
        return _sigma2_cache[cache_key]
        
    # Validamos que la tanda existe en nuestros datos
    if tanda_label not in tandas:
        raise ValueError(f"Etiqueta '{tanda_label}' no encontrada en los datos.")
        
    # --- Comienza el cálculo físico ---
    k = 2 * np.pi / wl
    elev_rad = np.radians(elev_deg)
    
    # Calculamos la longitud de camino correcta para cada ángulo
    L_path = np.where(elev_rad > 0, H_turb / np.sin(elev_rad), np.inf)
    
    # Obtenemos los datos de Cn² para la tanda seleccionada
    idx = np.where(tandas == tanda_label)[0][0]
    cn2_vals_for_tanda = cn2_table[:, idx]
    
    # Calculamos la tabla de sigma² para todos los ángulos
    sigma2_vals = 1.23 * (k**(7/6)) * cn2_vals_for_tanda * (L_path**(11/6))
    
    # Creamos la función de interpolación final: elev_rad -> sigma²
    f_sigma2 = interp1d(
        elev_rad,
        sigma2_vals,
        kind='linear',
        bounds_error=False,
        fill_value=(sigma2_vals[0], sigma2_vals[-1])
    )
    
    # Guardamos la función en el caché y la devolvemos
    _sigma2_cache[cache_key] = f_sigma2
    return f_sigma2