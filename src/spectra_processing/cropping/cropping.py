import numpy as np


def crop_spectra_absolute(spectral_map: np.ndarray, x_axis: np.ndarray, crop_start: float, crop_end: float) -> None:

    mask = (x_axis >= crop_start) & (x_axis <= crop_end)

    x_axis = x_axis[mask]
    spectral_map = spectral_map[..., mask]

    return spectral_map, x_axis


def crop_spectra_relative(spectral_map: np.ndarray, x_axis: np.ndarray, crop_first: int, crop_last: int) -> None:

    x_axis = x_axis[crop_first:-crop_last if crop_last > 0 else -1]
    spectral_map = spectral_map[..., crop_first:-crop_last if crop_last > 0 else -1]

    return spectral_map, x_axis


def crop_map(spectral_map: np.ndarray, left: int, top: int, right: int, bottom: int) -> None:
    
    # TODO: check top, bottom, left, right..
    spectral_map = spectral_map[top:bottom, left:right]

    return spectral_map
