import numpy as np
import scipy.interpolate as si
from typing import Tuple


def linearize(
    spectral_map: np.ndarray, x_axis: np.ndarray, step: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    A function to perform data linearization on the whole spectral map.
    That means that there will be equal steps between the data points.

    Parameters:
        step (float): Required step between the data points.
        TODO
    """

    spectrum_spline = si.CubicSpline(x_axis, spectral_map, axis=2, extrapolate=False)
    new_x = np.arange(np.ceil(x_axis[0]), np.floor(x_axis[-1]), step)
    x_axis = new_x
    spectral_map = spectrum_spline(new_x)

    return spectral_map, x_axis
