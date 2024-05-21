import numpy as np
from functools import reduce


def get_indices_range(x: np.ndarray, start_value: float, end_value: float) -> np.ndarray:
    """
    Function to get range of indices of (`start_value`, `end_value`) interval in the (sorted) `x` array.

    Parameters:
        x (np.ndarray): Sorted array in which to find the indices.
        start_value (float): Left bound of the interval.
        end_value (float): Right bound of the interval.
    """

    # get index of element closest to `start_value`
    start_index = np.argmin(np.absolute(x - start_value))

    end_index = np.argmin(np.absolute(x - end_value))

    # get all indices between
    return np.r_[start_index:end_index]


def get_indices_to_fit(x: np.ndarray, ranges_to_ignore: list[list[int]]) -> np.ndarray:
    """
    Function to get values of array `x` without values in `ranges_to_ingore`.

    Parameters:
        x (np.ndarray): Sorted array in which to ignore the values.
        ranges_to_ignore (list(list(int))): List of ranges to ignore. Example: [[2750, 3800], [3900, 4200]]
    """

    # union of indices that have to be ignored
    union = reduce(np.union1d, (get_indices_range(x, *i) for i in ranges_to_ignore))
    # get the exact opposite from `x` array
    to_fit = np.in1d(np.arange(x.shape[0]), union, invert=True)

    return to_fit


def get_no_water_indices(x: np.ndarray) -> np.ndarray:
    """
    Function to get indices of 'no water' elements, i.e. elements that are not in Raman water band.

    Parameters:
        x (np.ndarray): Sorted array in which to ignore the water band area.
    """

    to_ignore = [[2800, 3700]]  # possible C-H vibrations + water

    return get_indices_to_fit(x, to_ignore)
