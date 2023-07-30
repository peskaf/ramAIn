import numpy as np
from src.models.spectal_map import SpectralMap


def crop_spectra_absolute(spectral_map: SpectralMap, crop_start: float, crop_end: float) -> None:
    """
    The function to crop the data according to given parameters.

    Parameters:
        crop_start (float): Value on x axis from which to start cropping the spectra.
        crop_end (float): Value on x axis where to end cropping the spectra.
    """

    x_axis_start_idx = np.argmin(np.abs(spectral_map.x_axis - crop_start))
    x_axis_end_idx = np.argmin(np.abs(spectral_map.x_axis - crop_end))
    
    spectral_map.x_axis = spectral_map.x_axis[x_axis_start_idx:x_axis_end_idx+1]
    spectral_map.data = spectral_map.data[:, :, x_axis_start_idx:x_axis_end_idx+1]

    return spectral_map


def crop_spectra_relative(spectral_map: SpectralMap, crop_first: int, crop_last: int) -> None:
    """
    The function to crop the data according to given parameters.

    # TODO
    Parameters:
        crop_first (int): ...
        crop_last (int): ...
    """

    spectral_map.x_axis = spectral_map.x_axis[crop_first:-crop_last if crop_last > 0 else -1]
    spectral_map.data = spectral_map.data[:, :, crop_first:-crop_last if crop_last > 0 else -1]

    return spectral_map


def crop_map(spectral_map: SpectralMap, left: int, top: int, right: int, bottom: int) -> None:
    """
    The function to crop the data according to given parameters.

    Parameters:
        left (int): The left-most index from which to crop the spectral map (upper left corner x).
        top (int): The top-most index from which to crop the spectral map (upper left corner y).
        right (int): The right-most index to which to crop the spectral map (lower right corner x).
        bottom (int): The bottom-most index to which to crop the spectral map (lower right corner y).
    """

    spectral_map.data = spectral_map.data[left:right, top:bottom]

    return spectral_map
