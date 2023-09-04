import numpy as np   
from ...utils import math_morphology


def get_optimal_structuring_element_width(values: np.ndarray) -> int:
    """
    A function to compute optimal structuring element for the math morphology bg removal approach.
    Implementation of algorithm by Perez-Pueyo et al (doi: 10.1366/000370210791414281).

    Parameters:
        values (np.ndarray): Values for which to compute the optimal structuring elementd width.
    
    Returns:
        window_width (int): Optimal structuring element width.
    """

    # how many similar results have to occur to end the algorithm
    max_sim_counter = 3

    window_width = 1
    opened_array = math_morphology.opening(values, window_width)

    while True:
        window_width += 1
        new_opened_array = math_morphology.opening(opened_array, window_width)
        if np.any(new_opened_array != opened_array):
            similarity_counter = 0
            opened_array = new_opened_array
            continue
        else:
            similarity_counter += 1
            if similarity_counter == max_sim_counter:
                return window_width - max_sim_counter + 1 # restore window width of the first similar result


def _math_morpho_step(y: np.ndarray, window_width: int) -> np.ndarray:
    """
    One step of the math morpho bg subtraction algorithm.
    Implementation of algorithm by Perez-Pueyo et al (doi: 10.1366/000370210791414281).

    Parameters:
        y (np.ndarray): Values on which mathematical morphology methods are performed.
        window_width (int): Width of the structuring element for MM operations.

    Returns:
        result (np.ndarray): Values after one step of the alogrithm.
    """

    spectrum_opening = math_morphology.opening(y, window_width)
    approximation = np.mean(math_morphology.erosion(spectrum_opening, window_width) + math_morphology.dilation(spectrum_opening, window_width), axis=0)
    return np.minimum(spectrum_opening, approximation)


def _math_morpho_on_spectrum(spectrum: np.ndarray, x_axis: np.ndarray, ignore_water: bool) -> np.ndarray:
    """
    A function to perform math morpho algorithm on one spectrum, icluding water ignorance and signal emiting.
    Implementation of changed algorithm by Perez-Pueyo et al (doi: 10.1366/000370210791414281).

    Parameters:
        spectrum (np.ndarray): Spectrum on which the algorithm will be performed.
        x_axis (np.ndarray): TBD
        ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.

    Returns:
        result (np.ndarray): Estimated background of the provided spectrum `spectrum`.
    """

    if ignore_water:
        water_start_point = 2800
        water_start_index = np.argmin(np.abs(x_axis - water_start_point))

        water_part_y = spectrum[water_start_index:]
        not_water_part_y = spectrum[:water_start_index]

        window_width_water = int(np.round(len(water_part_y) / 3)) # TODO: best??
        window_width_no_water = get_optimal_structuring_element_width(not_water_part_y)

        bg_water = _math_morpho_step(water_part_y, window_width_water)
        bg_no_water = _math_morpho_step(not_water_part_y, window_width_no_water)

        background = np.concatenate((bg_no_water, bg_water))
        return background

    window_width = get_optimal_structuring_element_width(spectrum)

    spectrum_opening = math_morphology.opening(spectrum, window_width)
    approximation = np.mean(math_morphology.erosion(spectrum_opening, window_width) + math_morphology.dilation(spectrum_opening, window_width), axis=0)
    background = np.minimum(spectrum_opening, approximation)
    return background

def math_morpho(spectral_map: np.ndarray, x_axis: np.ndarray, ignore_water: bool) -> np.ndarray:
    """
    No speed-up version of the math morpho bg subtraction algorithm Perez-Pueyo et al (doi: 10.1366/000370210791414281)
    with version for water ignorance. Algorithm is performed on all spectra in the spectral map.

    Possible speed-ups: clustering for optimal structuring element estimation, multithreading.

    Parameters:
        TBD
        ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
    """

    backgrounds = np.apply_along_axis(_math_morpho_on_spectrum, 2, spectral_map, x_axis, ignore_water)
    spectral_map -= backgrounds

    return spectral_map
