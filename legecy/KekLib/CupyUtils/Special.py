"""
    CupyUtils.Special.py

    
"""
import cupy as cp
from scipy import special

def sici(x):
    si, ci = special.sici(cp.asnumpy(x))
    return cp.asarray(si), cp.asarray(ci)
