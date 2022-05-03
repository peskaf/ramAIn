import numpy as np

def erosion(values: np.ndarray, window_width: int) -> np.ndarray:
    # eroze -> minmum v okně
    padded_values = np.pad(values, (window_width, window_width), 'constant', constant_values=(values[0], values[-1])) # pad with side values from sides
    windows = np.lib.stride_tricks.sliding_window_view(padded_values, 2 * window_width + 1)
    mins = np.min(windows, axis=1)
    return mins

def dilation(values: np.ndarray, window_width: int) -> np.ndarray:
    # dilatace -> maximum v okně
    padded_values = np.pad(values, (window_width, window_width), 'constant', constant_values=(values[0], values[-1])) # pad with side values from sides
    windows = np.lib.stride_tricks.sliding_window_view(padded_values, 2 * window_width + 1)
    mins = np.max(windows, axis=1)
    return mins

def opening(values: np.ndarray, window_width: int) -> np.ndarray:
    return dilation(erosion(values, window_width), window_width)