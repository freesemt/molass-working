"""
    CupyUtils.CupyWrapper.ndimage.ndimage_wrapper.py

    
"""
import cupy as cp
import cupyx

def rotate(input, angle, axes=(1,0), reshape=True, output=None):
    return cp.asnumpy(cupyx.scipy.ndimage.rotate(cp.asarray(input), angle, axes, reshape, output))
