import numpy as np
from scipy.signal import savgol_filter


def savgol(
    spectral_map: np.ndarray, window_length: int = 5, polyorder: int = 2
) -> np.ndarray:
    spectral_map_ = spectral_map.view((-1, spectral_map.shape[2]))
    if spectral_map_.ndim != 2:
        raise ValueError("Input must be a 2D array")

    # Check if window_length is odd and greater than polyorder
    if window_length % 2 == 0 or window_length <= polyorder:
        raise ValueError("window_length must be odd and greater than polyorder")

    # Apply Savitzky-Golay filter to each spectrum
    smoothed_data = np.array(
        [
            savgol_filter(spectral_map_[i, :], window_length, polyorder)
            for i in range(spectral_map_.shape[0])
        ]
    )
    smoothed_data = smoothed_data.reshape(spectral_map.shape)
    return smoothed_data
