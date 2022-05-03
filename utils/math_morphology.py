import numpy as np


def erosion(values: np.ndarray, window_width: int) -> np.ndarray:
    """
    Function to get erosion of `values` array with structuring elements with `window_width` width.
    Erosion ... minimum in the sliding window.

    Parameters:
        values (np.ndarray): Array fo values that are to be eroded.
        window_width (int): Structuring element width, i.e. whole structuring element has size 2*`window_width` + 1
    """

    # pad with side values from sides -> minimum will be the same
    padded_values = np.pad(values, (window_width, window_width), 'constant', constant_values=(values[0], values[-1]))
    # view the array as the windows (window slides one position)
    windows = np.lib.stride_tricks.sliding_window_view(padded_values, 2*window_width + 1)
    # minimum from each window = erosion
    mins = np.min(windows, axis=1)

    return mins


def dilation(values: np.ndarray, window_width: int) -> np.ndarray:
    """
    Function to get dilatation of `values` array with structuring elements with `window_width` width.
    Dilatation ... maximum in the sliding window.

    Parameters:
        values (np.ndarray): Array fo values that are to be dilatated.
        window_width (int): Structuring element width, i.e. whole structuring element has size 2*`window_width` + 1
    """

    # pad with side values from sides -> maximum will be the same
    padded_values = np.pad(values, (window_width, window_width), 'constant', constant_values=(values[0], values[-1]))
    # view the array as the windows (window slides one position)
    windows = np.lib.stride_tricks.sliding_window_view(padded_values, 2*window_width + 1)
    # maximum from each window = dilatation
    maxes = np.max(windows, axis=1)

    return maxes


def opening(values: np.ndarray, window_width: int) -> np.ndarray:
    """
    Function to get opening of `values` array with structuring elements with `window_width` width.
    Opening ... dilatation of the erosion.

    Parameters:
        values (np.ndarray): Array fo values that are to be opened.
        window_width (int): Structuring element width, i.e. whole structuring element has size 2*`window_width` + 1
    """

    return dilation(erosion(values, window_width), window_width)
