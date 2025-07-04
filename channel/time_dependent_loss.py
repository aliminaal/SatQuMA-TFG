# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 00:13:57 2021

@author: Duncan McArthur
"""

from os.path import join
import numpy as np

from .diffraction.diffraction import diffract
from .orbital.circular_polarorbit import (elevation, distance, tMax, 
                                          get_xi_from_theta)
from .atmosphere.atmos_data import (make_f_atm, default_datafile)
# La importación ahora apunta a tu módulo de turbulencia corregido.
from .Turbulence.turbulencia import get_turbulence_for_angle

__all__ = ['interp_atm_data','time_dependent_losses','get_losses']

#############################################################################

def interp_atm_data(wl,datafile=None):
    """
    Generate an elevation dependent atmospheric transmissivity function by 
    interpolating data from a file.
    (Esta función no requiere cambios)
    """
    if datafile is None:
        datafile = default_datafile()
    f_atm = make_f_atm(datafile,wl)
    return f_atm

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def time_dependent_losses(R,hsat,xi,hOGS,wl,aT,aR,w0,f_atm,eta_int, loss_params):
    """
    Generate time dependent loss array based on diffraction, atmospheric,
    inherent system losses, and turbulence-induced scintillation.
    """
    # Constantes y parámetros del sistema (sin cambios)
    G           = 6.67430e-11
    M           = 5.9724e24
    k           = 2*np.pi / (wl*10**(-9))
    omega       = np.sqrt(G*M / (R + hsat)**3)
    OGScoords   = np.array([0,0,R + hOGS])

    # Inicialización de arrays
    tmax      = int(tMax(R,hsat,hOGS,omega,xi))
    # Se amplía el array de 7 a 9 columnas para incluir sigma2 y T_turb
    vals      = np.empty((2*tmax+1, 9))
    count     = 0
    
    # Comprobación de la turbulencia una vez antes del bucle para eficiencia
    turbulence_enabled = loss_params.get('turbulencia', False)

    for t in range(tmax,-tmax-1,-1):
        # Lógica orbital (sin cambios)
        elev_rad  = elevation(R+hsat,omega*t,xi,OGScoords)
        L         = distance(R+hsat,omega*t,xi,OGScoords)
    
        # Cálculo de pérdidas estáticas (sin cambios)
        eta_atm   = f_atm(elev_rad)
        eta_diff  = diffract(aT,aR,L,k,w0)
        
        # Bloque para calcular la turbulencia
        if turbulence_enabled:
            elev_deg = np.degrees(elev_rad)
            # Llamada a la nueva función de turbulencia
            sigma2, T_turb = get_turbulence_for_angle(elev_deg, loss_params)
        else:
            # Si la turbulencia está desactivada, los valores son neutros
            sigma2 = 0.0
            T_turb = 1.0

        # El cálculo de eta_tot ahora incluye el efecto fluctuante de la turbulencia
        eta_tot = eta_atm * eta_diff * eta_int * T_turb
        
        # Almacenamiento de datos, incluyendo las nuevas columnas
        vals[count,:] = [t, elev_rad, eta_tot, eta_diff, eta_atm, eta_int, L, sigma2, T_turb]
        count += 1
        
    # El encabezado se actualiza para reflejar las nuevas columnas
    header  = 'Time (s),Elevation (rad),eta_tot,eta_diff,eta_atm,eta_sys,Distance (m),sigma2,T_turb'
    return vals, header

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_losses(theta_max,loss_params,f_atm,tPrint,outpath):
    """
    Returns the loss array by either generating data or reading from file.
    (Esta función no requiere cambios en su lógica)
    """
    if loss_params.get('tReadLoss'):
        loss_file = loss_params['loss_file'].format(theta_max)
        if tPrint: print(f"Reading losses from file: {join(loss_params.get('loss_path', '.'), loss_file)}\n{'-'*60}")
        loss_data = np.loadtxt(join(loss_params.get('loss_path', '.'), loss_file), delimiter=',', skiprows=1, usecols=(0,1,loss_params.get('loss_col', 2)-1))
    else:
        if tPrint: print(f"Generating losses for theta_max = {np.degrees(theta_max)} deg\n{'-'*60}")
        xi = get_xi_from_theta(theta_max,loss_params['R_E'],loss_params['h_T'],loss_params['h_R'])
        loss_data, loss_head = time_dependent_losses(loss_params['R_E'],loss_params['h_T'],xi,loss_params['h_R'],loss_params['wvl'],loss_params['aT'],loss_params['aR'],loss_params['w0'],f_atm,loss_params['eta_int'],loss_params)
        if loss_params.get('tWriteLoss'):
            # Formateo de nombre de archivo mejorado para evitar errores
            loss_file = f"FS_loss_th_m_{np.degrees(theta_max):5.2f}_wl_{loss_params['wvl']:.0f}nm_h_{loss_params['h_T']/1e3:.0f}km_h1_{loss_params['h_R']/1e3:.0f}km_aT_{loss_params['aT']}m_aR_{loss_params['aR']}m_w0_{loss_params['w0']}m.csv"
            if tPrint: print(f"Saving losses to file: {join(outpath,loss_file)}\n{'-'*60}")
            np.savetxt(join(outpath,loss_file),loss_data,delimiter=',',header=loss_head)
    return loss_data