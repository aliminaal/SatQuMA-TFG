# -*- coding: utf-8 -*-
"""
Módulo para calcular la turbulencia y muestrear la transmisividad
en función del ángulo de elevación, usando el perfil Cn² interpolado.

Incluye:
  - Funciones de Rytov y parámetros Gamma-Gamma.
  - Muestreo de transmisividad (lognormal o Gamma-Gamma).
  - Función principal get_turbulence_for_angle().
"""

import numpy as np
from scipy.stats import lognorm
import numpy.random as npr

# Importar solo la parte de interpolación de Cn²
from .cn2_interpolacion import get_f_cn2

__all__ = [
    'sigma_rytov', 'gamma_gamma_params', 'sample_transmissivity',
    'get_turbulence_for_angle'
]


def sigma_rytov(cn2_val, k, L):
    """
    Calcula la varianza de Rytov (σ²) para un valor de Cn² dado:
      σ² = 1.23 * k^(7/6) * cn2_val * L^(11/6)

    Parameters
    ----------
    cn2_val : float
        Valor local de Cn² (m^(-2/3)).
    k : float
        Número de onda: k = 2π / λ (λ en metros).
    L : float
        Longitud de enlace en metros.

    Returns
    -------
    σ² : float
        Varianza de Rytov.
    """
    return 1.23 * (k**(7/6)) * cn2_val * (L**(11/6))


def gamma_gamma_params(sigma_R2):
    """
    Calcula los parámetros a, b del modelo Gamma-Gamma a partir de σ² de Rytov:
      a = 1 / [exp{0.49σ² / (1 + 1.11σ²^(12/5))^(7/6)} – 1]
      b = 1 / [exp{0.51σ² / (1 + 0.69σ²^(12/5))^(5/6)} – 1]

    Parameters
    ----------
    sigma_R2 : float
        Varianza de Rytov (σ²).

    Returns
    -------
    (a, b) : tuple de floats
        Parámetros a y b para la distribución Gamma-Gamma.
    """
    a = 1.0 / (np.exp(0.49 * sigma_R2 / (1 + 1.11 * sigma_R2**(12/5))**(7/6)) - 1)
    b = 1.0 / (np.exp(0.51 * sigma_R2 / (1 + 0.69 * sigma_R2**(12/5))**(5/6)) - 1)
    return a, b


def sample_transmissivity(cn2_val, k, L):
    """
    Muestra un valor de transmisividad atmosférica a partir de Cn² y longitud de enlace:
      - Si σ² < 1: modelo lognormal.
      - Si σ² ≥ 1: modelo Gamma-Gamma.

    Parameters
    ----------
    cn2_val : float
        Valor local de Cn² (m^(-2/3)).
    k : float
        Número de onda: k = 2π / λ.
    L : float
        Longitud de enlace en metros.

    Returns
    -------
    T : float
        Valor muestreado de transmisividad (≥ 0).
    """
    sigma2 = sigma_rytov(cn2_val, k, L)

    if sigma2 < 1.0:
        μ = -0.5 * sigma2
        s = np.sqrt(sigma2)
        return lognorm(s=s, scale=np.exp(μ)).rvs()
    else:
        a, b = gamma_gamma_params(sigma2)
        X = npr.gamma(shape=a, scale=1.0 / a)
        Y = npr.gamma(shape=b, scale=1.0 / b)
        return X * Y


def get_turbulence_for_angle(elev_deg, loss_params, wl, L):
    """
    Dado un ángulo de elevación en grados y parámetros de pérdida, devuelve:
      - cn2_loc  : Cn² interpolado en ese ángulo,
      - sigma2   : varianza de Rytov σ²,
      - T        : muestra de transmisividad.

    Si loss_params['turbulencia'] es False o loss_params['tReadLoss'] es True,
    devuelve (None, None, None).

    Parameters
    ----------
    elev_deg : float
        Ángulo de elevación en grados (0–90).
    loss_params : dict
        Debe contener:
          - 'turbulencia' (bool): si False, omite el cálculo.
          - 'tReadLoss' (bool): si True, omite el cálculo.
          - 'tanda_label' (str): etiqueta de tanda para interpolar Cn².
    wavelength : float
        Longitud de onda en metros (e.g. 785e-9 para 785 nm).
    L : float
        Longitud de enlace en metros.

    Returns
    -------
    (cn2_loc, sigma2, T) : tupla de floats o (None, None, None)
        - cn2_loc : valor de Cn² interpolado en elev_deg.
        - sigma2  : varianza de Rytov σ².
        - T       : valor muestreado de transmisividad.
    """
    if not loss_params.get('turbulencia', False):
        return None, None, None

    if loss_params.get('tReadLoss', False):
        return None, None, None

    # 1) Obtener función de interpolación de Cn² para la tanda indicada
    f_cn2 = get_f_cn2(loss_params)

    # 2) Convertir elevación a radianes y obtener Cn² local
    elev_rad = np.radians(elev_deg)
    cn2_loc = float(f_cn2(elev_rad))

    # 3) Calcular número de onda k = 2π / λ
    k = 2 * np.pi / wl

    # 4) Calcular σ² de Rytov
    sigma2 = sigma_rytov(cn2_loc, k, L)

    # 5) Muestrear transmisividad según σ²
    T = sample_transmissivity(cn2_loc, k, L)

    return cn2_loc, sigma2, T
