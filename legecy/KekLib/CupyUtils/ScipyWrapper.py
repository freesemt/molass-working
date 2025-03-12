"""
    CupyUtils.ScipyWrapper.py

    
"""

import numpy as np
import cupy as cp
from scipy import interpolate

class interp1d:
    def __init__(self, x, y, kind='linear', fill_value=None):
        self.scipy_obj = interpolate.interp1d(cp.asnumpy(x), cp.asnumpy(y), kind=kind, fill_value=fill_value)

    def __call__(self, x):
        y = self.scipy_obj(cp.asnumpy(x))
        return cp.asarray(y)
