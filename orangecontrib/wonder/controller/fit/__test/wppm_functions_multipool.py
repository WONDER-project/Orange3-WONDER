import numpy
import multiprocessing
from orangecontrib.wonder.controller.fit.wppm_functions import _wrapper_fit_function_direct

n_pools = multiprocessing.cpu_count() - 1
pool = multiprocessing.Pool(n_pools)

def fit_function_direct_multipool(twotheta, fit_global_parameters, diffraction_pattern_index = 0):
    args = [[twotheta, fit_global_parameters, diffraction_pattern_index] for twotheta in numpy.array_split(twotheta, n_pools)]

    return numpy.concatenate(pool.map(_wrapper_fit_function_direct, args))
