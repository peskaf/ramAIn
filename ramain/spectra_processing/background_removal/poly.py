import numpy as np
from ramain.utils import indices


def poly_bg(
    spectrum: np.ndarray, x_axis: np.ndarray, degree: int, ignore_water: bool = True
) -> np.ndarray:
    """
    A function to perform simple polynomial interpolation on the spectrum to estimate the backgrounds.
    Water can be ingored.

    Parameters:
        y (np.ndarray): Spectrum on which the algorithm will be performed.
        degree (int): Degree of the polynomial used for interpolation.
        ignore_water (bool): Info whether variation of the algo with water ignorace should be performed. Default: True.

    Returns:
        result (np.ndarray): Estimated background of the provided spectrum `y`.
    """
    x = x_axis

    if ignore_water:
        no_water_indices = indices.get_no_water_indices(x)
        x = x[no_water_indices]
        spectrum = spectrum[no_water_indices]

    poly_obj = np.polynomial.Polynomial(None).fit(x, spectrum, deg=degree)
    # NOTE: ploynomial has to be evaluated at every point of `x_axis` here as it is background for the whole spectrum
    return poly_obj(x_axis)


def poly(
    spectral_map: np.ndarray, x_axis: np.ndarray, degree: int, ignore_water: bool
) -> np.ndarray:
    """
    A function to perform polynomial background estimation and subtraction on the whole
    spectral map.

    Parameters:
        degree (int): Degree of the polynomial used for interpolation.
        ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
    """

    backgrounds = np.apply_along_axis(
        poly_bg, 2, spectral_map, x_axis, degree, ignore_water
    )
    spectral_map -= backgrounds

    return spectral_map
