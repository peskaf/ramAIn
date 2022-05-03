import numpy as np
from functools import reduce

def _get_indices_range(x, start_value, end_value) -> np.ndarray:
    start_index = np.argmin(np.absolute(x - start_value))
    end_index = np.argmin(np.absolute(x - end_value))
    return np.r_[start_index:end_index]

def _get_indices_to_fit(x, ranges_to_ignore) -> np.ndarray:
    union = reduce(np.union1d, (_get_indices_range(x, *i) for i in ranges_to_ignore))
    to_fit = np.in1d(np.arange(x.shape[0]), union, invert=True)
    return to_fit

def _get_no_water_indices(x: np.ndarray) -> np.ndarray:
    to_ignore = [[2750, 3750]] # possible C-H vibrations included
    return _get_indices_to_fit(x, to_ignore)