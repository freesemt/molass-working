"""
    CupyUtils.CupyWrapper.fft.fft_wrapper.py

    
"""
import cupy as cp

def fftn(a, s=None, axes=None, norm=None):
    return cp.asnumpy(cp.fft.fftn(cp.asarray(a), s, axes, norm))

def ifftn(a, s=None, axes=None, norm=None):
    return cp.asnumpy(cp.fft.ifftn(cp.asarray(a), s, axes, norm))
