import numpy as np
import cupy as cp

def searchsorted(a, v, side='left', sorter=None):
    assert sorter is None

    np_a = cp.asnumpy(a)
    np_v = cp.asnumpy(v)
    ret = np.searchsorted(np_a, np_v, side, sorter)
    return cp.asarray(ret)

def interp(x, xp, fp, left=None, right=None, period=None):
    assert left is None
    assert right is None
    assert period is None

    np_x = cp.asnumpy(x)
    np_xp = cp.asnumpy(xp)
    np_fp = cp.asnumpy(fp)
    y = np.interp(np_x, np_xp, np_fp, left, right, period)
    return cp.asarray(y)

def in1d(ar1, ar2, assume_unique=False, invert=False):
    np_ar1 = cp.asnumpy(ar1)
    np_ar2 = cp.asnumpy(ar2)
    ret = np.in1d(np_ar1, np_ar2, assume_unique, invert)
    return cp.asarray(ret)
