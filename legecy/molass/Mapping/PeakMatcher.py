"""
    Mapping.PeakMatcher.py

    
"""
import numpy as np
from itertools import combinations
from scipy.stats import linregress

def combination_pairs(m, n):
    assert m != n
    more_indeces = np.arange(max(m, n))
    num = min(m, n)
    less_indeces = np.arange(num)
    for c in combinations(more_indeces, num):
        if m > n:
            yield list(c), less_indeces
        else:
            yield less_indeces, list(c)

def evaluate_matching(xr_x, uv_x, x, y):
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    mapped_xr_ends = []
    for px in xr_x[[0, -1]]:
        mapped_xr_ends.append(px*slope + intercept)
    uv_minx = max(uv_x[0], mapped_xr_ends[0])
    uv_maxx = min(uv_x[-1], mapped_xr_ends[1])
    # y = ax + b
    # x = (y - b)/a
    a_ = 1/slope
    b_ = -intercept/slope
    mapped_uv_ends = []
    for px in uv_minx, uv_maxx:
        mapped_uv_ends.append(px*a_ + b_)
    xr_minx = max(xr_x[0], mapped_uv_ends[0])
    xr_maxx = max(xr_x[-1], mapped_uv_ends[1])
    covered_ratio = (xr_maxx - xr_minx)/(xr_x[-1] - xr_x[0])
    score = 1/covered_ratio

    if len(x) > 2:
        score *= p_value
    else:
        # do not use p_value since it is zero
        pass

    return score

def select_matching_peaks(xr_x, xr_peaks, uv_x, uv_peaks, debug=False):
    if debug:
        print("len(xr_peaks)=", len(xr_peaks))
        print("len(uv_peaks)=", len(uv_peaks))
    xr_peaks = np.asarray(xr_peaks)
    uv_peaks = np.asarray(uv_peaks)

    # evaluate all the combination pairs
    score_recs = []
    for index1, index2 in combination_pairs(len(xr_peaks), len(uv_peaks)):
        score = evaluate_matching(xr_x, uv_x, xr_x[xr_peaks[index1]], uv_x[uv_peaks[index2]])
        if debug:
            print(index1, index2, score)
        score_recs.append((index1, index2, score))
    
    score_recs = sorted(score_recs, key=lambda x: x[2])
    index1, index2, score = score_recs[0]   # the record with smallest p_value
    return xr_peaks[index1], uv_peaks[index2]