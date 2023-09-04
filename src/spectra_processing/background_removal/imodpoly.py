import numpy as np
from ...utils import indices


def imodpoly_poly_bg(spectrum: np.ndarray, x_axis: np.ndarray, degree: int, ignore_water: bool = True) -> np.ndarray:
    """
    Implementation of I-ModPoly algorithm for bg subtraction (Zhao et al, doi: 10.1366/000370207782597003), added vaersion
    with possible water ignorance and signal emission.

    Parameters:
        y (np.ndarray): Spectrum on which the algorithm will be performed.
        TODO
        degree (int): Degree of the polynomial used for interpolation.
        ignore_water (bool): Info whether variation of the algo with water ignorace should be performed. Default: True.

    Returns:
        result (np.ndarray): Estimated background of the provided spectrum `y`.
    """

    x = x_axis

    # ignore indices of water
    if ignore_water:
        no_water_indices = indices.get_no_water_indices(x)
        x = x[no_water_indices]
        spectrum = spectrum[no_water_indices]

    signal = spectrum
    first_iter = True
    devs = [0]
    criterium = np.inf

    # algorithm based on the article
    while criterium > 0.05:
        poly_obj = np.polynomial.Polynomial(None).fit(x, signal, deg=degree)
        poly = poly_obj(x)
        residual = signal - poly
        residual_mean = np.mean(residual)
        DEV = np.sqrt(np.mean((residual - residual_mean)**2))
        devs.append(DEV)
        
        if first_iter: # remove peaks from fitting in first iteration
            not_peak_indices = np.where(signal <= (poly + DEV))
            signal = signal[not_peak_indices]
            x = x[not_peak_indices]
            first_iter = False
        else: # reconstruction
            signal = np.where(signal < poly + DEV, signal, poly + DEV)
        criterium = np.abs((DEV - devs[-2]) / DEV)

    # NOTE: ploynomial has to be evaluated at every point of `x_axis` here as it is background for the whole spectrum
    return poly_obj(x_axis)

def imodpoly(spectral_map: np.ndarray, x_axis: np.ndarray, degree: int, ignore_water: bool = True) -> np.ndarray:
    """
    A function that applies the I-ModPoly algorithm on the whole spectral map. Zhao et al (doi: 10.1366/000370207782597003)

    Parameters:
        degree (int): Degree of the polynomial used for interpolation.
        TODO
        ignore_water (bool): Info whether variation of the algo with water ignorace should be performed. Default: True.
    """

    backgrounds = np.apply_along_axis(imodpoly_poly_bg, 2, spectral_map, x_axis, degree, ignore_water)
    spectral_map -= backgrounds

    return spectral_map