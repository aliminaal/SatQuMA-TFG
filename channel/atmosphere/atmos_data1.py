# -*- coding: utf-8 -*-
"""

@author: Modified for Simulations Without MODTRAN Data
"""

import numpy as np

__all__ = ['get_f_atm', 'make_f_atm_parametric']


###############################################################################

def make_f_atm_parametric(wl):
    """
    Create a parametric atmospheric transmission efficiency (loss) function
    without using MODTRAN data.

    Parameters
    ----------
    wl : float
        The specific wavelength (nm).

    Returns
    -------
    f_atm : function
        Atmospheric transmissivity function.
    """

    # Define a parametric model for atmospheric losses
    def f_atm(elevation_angle):
        """
        Simulate atmospheric transmissivity based on elevation angle.

        Parameters
        ----------
        elevation_angle : float
            Elevation angle in radians.

        Returns
        -------
        transmissivity : float
            Simulated transmissivity (0 to 1).
        """
        # Example parameters (adjust for your system)
        base_transmissivity = 0.8  # Base transmissivity at zenith
        angular_loss_factor = 0.05  # Angular loss increase per radian

        # Loss increases with lower elevation angles
        transmissivity = base_transmissivity - angular_loss_factor * np.degrees(elevation_angle)
        # Ensure transmissivity is within [0, 1]
        return np.clip(transmissivity, 0, 1)

    return f_atm


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_f_atm(loss_params):
    """
    Returns an atmospheric transmissivity function with an elevation angle
    dependence. Uses a parametric model when MODTRAN data is unavailable.

    Parameters
    ----------
    loss_params : dict
        Dictionary of loss parameters.

    Returns
    -------
    f_atm : function
        Atmospheric transmissivity angular function.
    """
    if loss_params.get('tReadLoss', False):
        # Function not required so use dummy
        f_atm = lambda *args, **kwargs: None
    else:
        # Use the parametric model if no file is provided
        f_atm = make_f_atm_parametric(loss_params['wvl'])
    return f_atm
