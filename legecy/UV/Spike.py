# coding: utf-8
"""
    UV.Spike.py

    Copyright (c) 2022, SAXS Team, KEK-PF
"""
import numpy as np
import logging
import DebugPlot as plt
from .UvPreRecog import UvPreRecog

def spike(in_folder, logger, fig_file=None):
    from _MOLASS.SerialSettings import set_setting
    from Batch.StandardProcedure import StandardProcedure
    from Trimming.PreliminaryRecognition import PreliminaryRecognition

    set_setting("in_folder", in_folder)
    sp = StandardProcedure()
    sd = sp.load_old_way(in_folder)
    pre_recog = PreliminaryRecognition(sd)

    upr = UvPreRecog(sd, pre_recog, debug=True, fig_file=fig_file)
    upr.get_trim_slice()

    fc = pre_recog.flowchange
    a_curve2 = fc.a_curve2
    x = a_curve2.x
    y = a_curve2.y
    base_curve, params = upr.get_base_curve_info()
    residual_ratio = np.linalg.norm(base_curve(x, params) - y)/np.linalg.norm(y)
    return residual_ratio
