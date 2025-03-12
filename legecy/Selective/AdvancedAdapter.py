"""
    Selective.AdvancedAdapter.py

    Copyright (c) 2024, SAXS Team, KEK-PF
"""

def adapted_decompose_elution_simply(self):
    from KekLib.BasicUtils import Struct
    from importlib import reload
    import CFSD.SimpleDecompose
    reload(CFSD.SimpleDecompose)
    from CFSD.SimpleDecompose import decompose_elution_simply
    x = self.corbase_info.x
    y = self.corbase_info.y
    dialog = self.dialog
    min_frame = dialog.frames[dialog.min_index]
    uv_y = min_frame.uv_y
    num_peaks = len(min_frame.opt_recs)
    traditional_info = Struct(num_peaks=num_peaks, mapper=min_frame.mapper)
    decomp_result = decompose_elution_simply(x, y, uv_y, self.model, traditional_info)
    return decomp_result