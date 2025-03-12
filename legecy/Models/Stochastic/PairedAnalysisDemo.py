"""
    Models.Stochastic.PairedAnalysisDemo.py

    Copyright (c) 2024, SAXS Team, KEK-PF
"""
from importlib import reload

def prepare_data(input_folders, exec_spec):
    import Batch.BatchUtils
    reload(Batch.BatchUtils)
    from Batch.BatchUtils import load_lrfsrc

    use_mapping = exec_spec.get('use_mapping')

    info_list = []
    for k, folder in enumerate(input_folders):
        if k == 1 and use_mapping is not None and use_mapping:
            from Batch.BatchMappingUtils import load_lrfsrc_with_mapping
            lrfsrc = load_lrfsrc_with_mapping(folder, lrfsrc)
        else:
            lrfsrc = load_lrfsrc(folder)
        info_list.append((folder, lrfsrc))
    return info_list

def debug_main():
    import KekLib.DebugPlot as plt
    import Models.Stochastic.PairedAnalysisSpecs as specs
    reload(specs)
    from Models.Stochastic.PairedAnalysisSpecs import get_exec_spec

    exec_spec = get_exec_spec(3)
    input_folders   = exec_spec["input_folders"]

    info_list = prepare_data(input_folders, exec_spec)
    def paired_analysis():
        import Models.Stochastic.PairedAnalysis
        reload(Models.Stochastic.PairedAnalysis)
        from Models.Stochastic.PairedAnalysis import paired_analysis_main
        try:
            paired_analysis_main(info_list, exec_spec)
        except:
            from KekLib.ExceptionTracebacker import log_exception
            log_exception(None, "paired_analysis_impl: ")

    extra_button_specs = [
                    ("Paired Analysis", paired_analysis)
                    ]

    with plt.Dp(button_spec=["OK", "Cancel"],
                extra_button_specs=extra_button_specs):
        fig, ax = plt.subplots()
        plt.show()

def demo():
    from KekLib.OurTkinter import Tk
    root = Tk.Tk()
    root.withdraw()
    def demo_impl():
        debug_main()
        root.quit()
    root.after(100, demo_impl)
    root.mainloop()

if __name__ == "__main__":
    import sys
    sys.path.append("../lib")
    from KekLib.OurMatplotlib import mpl_1_5_backward_compatible_init
    mpl_1_5_backward_compatible_init()
    demo()