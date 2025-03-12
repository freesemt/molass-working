# coding: utf-8
"""
    CurveDecomposer.py

    Copyright (c) 2020, SAXS Team, KEK-PF
"""
from Models.ElutionCurveModels import EGH
from ElutionDecomposer import ElutionDecomposer

def decompose(ecurve, model=EGH()):
    x = ecurve.x
    y = ecurve.y
    decomposer = ElutionDecomposer(ecurve, x, y, model=model, retry_valley=True, deeply=True)
    return decomposer.fit_recs
