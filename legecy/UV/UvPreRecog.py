"""
    UV.UvPreRecog.py

    Copyright (c) 2022-2024, SAXS Team, KEK-PF
"""
import numpy as np
from scipy.optimize import minimize, basinhopping
import logging
import KekLib.DebugPlot as plt
from .PlainCurve import make_secondary_e_curve_at
from Trimming.FlowChangeCandidates import get_largest_gradients
from Trimming.Sigmoid import ex_sigmoid
from Peaks.EghSupples import egh, d_egh
from KekLib.SciPyCookbook import smooth
from KekLib.BasicUtils import Struct

USE_SPLINE_MODEL = True

class UvPreRecog:
    def __init__(self, sd, pre_recog, debug=False, fig_file=None):
        if USE_SPLINE_MODEL:
            if debug:
                from importlib import reload
                import Baseline.UvBaseSpline
                reload(Baseline.UvBaseSpline)
            from Baseline.UvBaseSpline import UvBaseSpline
        else:
            from Baseline.UvBaseCurve import UvBaseCurve

        self.logger = logging.getLogger(__name__)

        fc = pre_recog.flowchange
        a_curve = fc.a_curve
        a_curve2 = fc.a_curve2

        x = a_curve2.x
        y = a_curve2.y

        fc_points = fc.get_real_flow_changes()
        fc_point = fc_points[0]

        pp_, ppe, ret_slice = fc.remove_irregular_points()

        if USE_SPLINE_MODEL:
            base_curve = UvBaseSpline(sd, a_curve)
            params = base_curve.guess_params(a_curve2, pp_, ret_slice, fc_point=fc_point, debug=debug)
        else:
            base_curve = UvBaseCurve(sd, a_curve, 1, 1)
            params = base_curve.guess_params(a_curve2, pp_, ret_slice, debug=debug)

        if debug:
            from Baseline.Constants import SLOPE_SCALE
            from UV.PlainCurveUtils import get_both_wavelengths

            exsig_params = params.copy()
            exsig_params[4:6] /= SLOPE_SCALE
            w1, w2 = get_both_wavelengths(sd.lvector)
            gy = fc.gy
            with plt.Dp():
                from SerialAnalyzer.DataUtils import get_in_folder
                from Elution.CurveUtils import simple_plot
                from DataStructure.MatrixData import simple_plot_3d
                data = sd.conc_array
                wv = sd.lvector

                wide_figure = False

                figsize = (20,5) if wide_figure else (20, 5)
                fig = plt.figure(figsize=figsize)
                if wide_figure:
                    ax1 = fig.add_subplot(141, projection="3d")
                    ax2 = fig.add_subplot(142)
                    ax3 = fig.add_subplot(143)
                    ax4 = fig.add_subplot(144)
                else:
                    ax2 = fig.add_subplot(141)
                    ax21 = fig.add_subplot(142)
                    ax22 = fig.add_subplot(143)
                    ax3 = fig.add_subplot(144)

                fig.suptitle("UV Baseline Model Fitting for %s" % get_in_folder(), fontsize=20)
                if wide_figure:
                    ax1.set_title("3D View", fontsize=16)
                ax2.set_title("Elution at λ=%.3g" % w1, fontsize=16)
                ax3.set_title("Elution at λ=%.3g" % w2, fontsize=16)
                if wide_figure:
                    ax4.set_title("Gradient at λ=%.3g" % w2, fontsize=16)
                else:
                    for ax in [ax21, ax22, ax3]:
                        ax.set_title("Elution at λ=%.3g" % w2, fontsize=16)

                if wide_figure:
                    simple_plot_3d(ax1, data, x=wv)

                simple_plot(ax2, a_curve)
                ax3.plot(x, y, label="data")
                ax3.plot(x, base_curve(x, params, y), label="baseline model")
                ax3.legend()
                if wide_figure:
                    ax4.plot(x, gy)
                    for k in pp_:
                        ax4.plot(x[k], gy[k], "o")
                    if len(ppe) > 0:
                        ax4.plot(x[ppe], gy[ppe], "o", color="red", label="irregular")
                    ax4.legend()
                else:
                    ax21.plot(x, y, label="data")
                    ax21.plot(x, ex_sigmoid(x, *exsig_params[0:6]), label="ex_sigmoid")
                    ax21.plot(x, base_curve.diff_spline(x), y, label="derivative")
                    ax21.legend()
                    ax22.plot(x, y, label="data")
                    ax22.plot(x, ex_sigmoid(x, *exsig_params[0:6]), label="ex_sigmoid")
                    ax22.plot(x, params[6]*base_curve.diff_spline(x), label="scaled derivative")
                    ymin, ymax = ax22.get_ylim()
                    tx = x[-1]*0.7
                    ty = (ymin + ymax)/2
                    # ty = 0.2*ymin + 0.8*ymax
                    ax22.text(tx, ty, "Scale=%.2g" % params[6], fontsize=16, alpha=0.5)
                    ax22.legend()
                fig.tight_layout()

                if fig_file is None:
                    plt.show()
                else:
                    from time import sleep
                    fig.savefig(fig_file)
                    plt.show(block=False)
                    sleep(0.5)

        self.trim_slice = ret_slice
        self.base_curve = base_curve
        self.init_params = params

    def remove_irregular_points(self, x, y, gy, pp3):
        ret_pp = []
        err_pp = []
        for k in pp3:
            if k < len(y) - 10:
                ret_pp.append(k)
            else:
                err_pp.append(k)
        if len(err_pp) > 0:
            ret_slice = slice(None, np.min(err_pp))
        else:
            ret_slice = slice(None, None)
        return np.array(sorted(ret_pp, key=lambda j: -abs(gy[j]))), np.array(err_pp), ret_slice

    def get_trim_slice(self):
        return self.trim_slice

    def get_base_curve_info(self):
        return self.base_curve, self.init_params
