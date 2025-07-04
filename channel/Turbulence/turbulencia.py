# -*- coding: utf-8 -*-
"""
Módulo para calcular la turbulencia y muestrear la transmisividad
en función del ángulo de elevación.

Utiliza un modelo físicamente coherente que interpola la varianza de Rytov (sigma²)
pre-calculada para cada ángulo, en lugar de un Cn² puntual.
"""
import numpy as np
from scipy.stats import lognorm
# Importamos la nueva función que nos devuelve el interpolador de sigma².
from .cn2_interpolacion import get_f_sigma2

# Es una buena práctica usar un generador de números aleatorios moderno y explícito.
rng = np.random.default_rng()

# La única función que este módulo necesita "exportar" es la principal.
__all__ = ['get_turbulence_for_angle']


def _gamma_gamma_params(sigma_R2):
    """
    Calcula los parámetros a, b del modelo Gamma-Gamma de forma robusta.
    Función interna, no se exporta.
    """
    # Se usa np.errstate para evitar warnings si sigma_R2 es muy grande.
    with np.errstate(over='ignore', invalid='ignore'):
        a_denom = np.exp(0.49 * sigma_R2 / (1 + 1.11 * sigma_R2**(12/5))**(7/6)) - 1
        b_denom = np.exp(0.51 * sigma_R2 / (1 + 0.69 * sigma_R2**(12/5))**(5/6)) - 1
    
    # Si el denominador es cero o negativo, el parámetro es infinito (turbulencia extrema).
    a = 1.0 / a_denom if a_denom > 0 else np.inf
    b = 1.0 / b_denom if b_denom > 0 else np.inf
    return a, b


def _sample_transmissivity(sigma2):
    """
    Muestra un valor de transmisividad atmosférica a partir de una sigma² ya calculada.
    Función interna, no se exporta.
    """
    if sigma2 <= 0:
        return 1.0  # No hay fluctuaciones si no hay turbulencia.

    if sigma2 < 1.0:
        # Régimen de turbulencia débil -> Lognormal
        mu = -0.5 * sigma2
        s = np.sqrt(sigma2)
        # Usamos el generador moderno rng
        return lognorm.rvs(s=s, scale=np.exp(mu), random_state=rng)
    else:
        # Régimen de turbulencia fuerte -> Gamma-Gamma
        a, b = _gamma_gamma_params(sigma2)
        
        # Si los parámetros no son válidos (infinitos), la señal se ha perdido.
        if not (np.isfinite(a) and np.isfinite(b) and a > 0 and b > 0):
            return 0.0  # Desvanecimiento completo.
            
        # Muestreamos de dos distribuciones Gamma para obtener la Gamma-Gamma.
        X = rng.gamma(shape=a, scale=1.0 / a)
        Y = rng.gamma(shape=b, scale=1.0 / b)
        return X * Y


def get_turbulence_for_angle(elev_deg, loss_params):
    """
    Dado un ángulo de elevación y los parámetros del sistema, devuelve la
    varianza de Rytov y una muestra de transmisividad fluctuante.
    """
    # 1. Obtener la función de interpolación de sigma² (f(elev_rad) -> sigma²).
    try:
        f_sigma2 = get_f_sigma2(loss_params)
    except ValueError as e:
        print(f"Error al configurar la turbulencia: {e}")
        return None, None

    # 2. Convertir el ángulo de elevación a radianes.
    elev_rad = np.radians(elev_deg)

    # 3. Obtener el valor de sigma² para este ángulo específico.
    sigma2 = float(f_sigma2(elev_rad))

    # 4. Muestrear la transmisividad usando el valor de sigma².
    T = _sample_transmissivity(sigma2)

    # 5. Devolver los dos valores físicos relevantes.
    return sigma2, T