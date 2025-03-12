"""
    Particles.SmcSolver.py

    Copyright (c) 2024, SAXS Team, KEK-PF    
"""
import logging
from importlib import reload
import numpy as np
import pymc as pm
from Optimizer.StateSequence import save_opt_params
from Optimizer.OptimizerUtils import OptimizerResult

class SmcSolver:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.cb_fh = optimizer.cb_fh
        self.nfev = 0
        self.logger = logging.getLogger(__name__)
    
    def minimize(self, objective, init_params, niter=100, seed=1234, bounds=None, callback=None):
        self.objective = objective

        lower = bounds[:,0]
        upper = bounds[:,1]

        with pm.Model() as no_grad_model:
            # uniform priors on params
            params = pm.Uniform(
                "params",
                shape=len(init_params),
                lower=lower,
                upper=upper,
                initval=init_params,
            )

            import SMC.SolverDist
            reload(SMC.SolverDist)
            from SMC.SolverDist import create_custom_dist
            size = len(init_params)
            likelihood = create_custom_dist(objective, lower, upper, size, params)

        try:
            no_grad_model.compile_dlogp()
        except Exception as exc:
            print(type(exc))

        # import SMC.smc.sampling
        # reload(SMC.smc.sampling)
        # import SMC.smc.sampling as pmt

        with no_grad_model:
            # Use custom number of draws to replace the HMC based defaults
            idata_no_grad = pm.sample_smc(100)
            # idata_no_grad = pm.sample_smc(100, cores=1)
            # idata_no_grad = pm.sample_smc(100, kernel=pm.smc.MH)
            # idata_no_grad = pm.sample_smc(100, kernel=pm.smc.IMH)
            # idata_no_grad = pm.sample(100)
 
        return OptimizerResult(x=init_params, nit=niter, nfev=self.nfev)

    def callback(self, norm_params, f, accept):
        real_params = self.optimizer.to_real_params(norm_params)
        fv = self.objective(real_params)
        self.logger.info("callback: fv=%.3g", fv)
        save_opt_params(self.cb_fh, real_params, fv, accept, self.nfev)
        return False
