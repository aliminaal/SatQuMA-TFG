# -*- coding: utf-8 -*-
"""
Módulo para obtener una función de interpolación Cn²(elev_rad)
a partir de una tanda específica.
"""

import numpy as np
from scipy.interpolate import interp1d

# Importar tandas, elev y cn2 desde tu módulo de datos (datos_cn2.py)
from .pasosCn2 import tandas, elev, cn2

__all__ = ['make_f_cn2_local', 'get_f_cn2']


def make_f_cn2_local(tanda_label):
    """
    Crea una función de interpolación Cn² vs. elevación (en radianes)
    para la tanda especificada.

    Parameters
    ----------
    tanda_label : str
        Etiqueta de la tanda, p.e. 'tanda3_14.05'.

    Returns
    -------
    f_cn2 : callable
        Función que acepta un ángulo de elevación en radianes y devuelve
        el valor de Cn² interpolado en ese ángulo.
    """
    if tanda_label not in tandas:
        raise ValueError(f"Etiqueta '{tanda_label}' no encontrada en tandas")
    idx = np.where(tandas == tanda_label)[0][0]
    cn2_vals = cn2[:, idx]  # 91 valores de Cn² para ángulos de elevación 0…90 (grados)

    # 1) calculamos array de θ_cenital en grados: θ_cen[i] = 90 - elev[i]
    theta_cen_deg = 90.0 - elev  # array de 90→0,89→1,…,0→90

    # 2) convertimos a radianes:
    theta_cen_rad = np.radians(theta_cen_deg)

    # Interpolación lineal; fuera de rango, devuelve cn2_vals[0] o cn2_vals[-1]
    f_cn2 = interp1d(
        theta_cen_rad,   # pasa elev (grados) → radianes
        cn2_vals,           # valores de Cn²
        kind='linear',
        bounds_error=False,
        fill_value=(cn2_vals[0], cn2_vals[-1])
    )
    return f_cn2


def get_f_cn2(loss_params):
    """
    Devuelve una función f_cn2(elev_rad) que interpola Cn² según la tanda indicada.
    Si loss_params['tReadLoss'] es True, devuelve una función dummy.

    Parameters
    ----------
    loss_params : dict
        Debe contener:
          - 'tReadLoss' (bool): si True, devuelve función dummy.
          - 'tanda_label' (str): etiqueta de tanda para interpolar Cn².
    """
    if not loss_params.get('turbulencia', False):
        return lambda *args, **kwargs: None

    if loss_params.get('tReadLoss', False):
        return lambda *args, **kwargs: None

    tanda = loss_params.get('tanda_label', '')
    if tanda == '':
        raise ValueError("Para get_f_cn2, debes especificar 'tanda_label' en loss_params")
    return make_f_cn2_local(tanda)
