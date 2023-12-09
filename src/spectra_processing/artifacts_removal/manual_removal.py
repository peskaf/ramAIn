import numpy as np


def interpolate_within_range(
    spectrum: np.ndarray, x_axis: np.ndarray, start: float, end: float
) -> None:
    start_idx = np.argmax((x_axis >= start))
    end_idx = x_axis.shape[0] - np.argmax((x_axis[::-1] <= end)) - 1

    # get end-points of the interpolation
    start_value = spectrum[start_idx]
    end_value = spectrum[end_idx]

    values_count = end_idx - start_idx + 1

    # interpolation
    new_values = np.linspace(start_value, end_value, num=values_count)
    spectrum[start_idx : end_idx + 1] = new_values

    return spectrum
