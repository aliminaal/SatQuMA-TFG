# -*- coding: utf-8 -*-
"""
Created on Tue May  2 15:45:03 2023

@author: Duncan McArthur
"""

import numpy as np

__all__ = ['gamma','h','heaviside']

###############################################################################

def h(x):
    """
    Evaluates the binary entropy function.
    Defined after Eq. (1) in [1].

    Parameters
    ----------
    x : float
        Function argument.

    Returns
    -------
    h : float
        Binary entropy.

    """

    h = -x * np.log2(x) - (1 - x) * np.log2(1 - x)
    return h

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def gamma(a,b,c,d):
    """
    Correction term. More info?
    Defined after Eq. (5) in [1].

    Parameters
    ----------
    a : float
        Argument 1.
    b : float
        Argument 2.
    c : float
        Argument 3.
    d : float
        Argument 4.

    Returns
    -------
    g : float
        Output value.

    """
    g1 = max((c + d) * (1 - b) * b / (c*d * np.log(2)), 0.0)
    g2 = max((c + d) * 21**2 / (c*d * (1 - b) * b*a**2), 1.0)
    g  = np.sqrt(g1 * np.log2(g2))
    return g

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def heaviside(x):
    """
    Heaviside step function: x -> x'\in{0,1}

    Parameters
    ----------
    x : float
        Argument, to be corrected using the step function.

    Returns
    -------
    integer
        Binary step output.

    """
    if (x < 0):
        return 0
    else:
        if (x > 0):
            return 1
        else:
            return 0.5