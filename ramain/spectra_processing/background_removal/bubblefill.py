# Source: https://github.com/mr-sheg/orpl/blob/main/src/orpl/baseline_removal.py
# Ajusted a little for our needs

from typing import Tuple

import numpy as np
from scipy.signal import savgol_filter
from . import njit

from PySide6.QtCore import Signal


# Bubblefill
@njit(cache=True)
def grow_bubble(
    spectrum: np.ndarray, alignment: str = "center"
) -> Tuple[np.ndarray, int]:
    """
    grow_bubble grows a bubble until it touches a spectrum.

    Usage
    -----
    bubble, touching_point = grow_bubble(spectrum, alignment)

    Parameters
    ----------
    spectrum : np.ndarray
        the input spectrum
    alignment : str, optional
        the alignment of the bubble to be grown. Possible values are
        ['left', 'right' and 'center'].
        If 'left', the bubble will be centered in x=0 and will have a width
        of 2x len(spectrum)
        If 'right', the bubble will be centered in x=len(spectrum) and will
        have a width of 2x len(spectrum)
        If 'center', the bubble will be centered in x=len(spectrum)/2 and
        will have a width of len(spectrum)
        , by default "center"

    Returns
    -------
    bubble : np.ndarray
        the grown bubble
    touching_point : int
        the x-coordinate where it touched the spectrum and *popped*.
    """
    xaxis = np.arange(len(spectrum))

    # Ajusting bubble parameter based on alignment
    if alignment == "left":
        # half bubble right
        width = 2 * len(spectrum)
        middle = 0
    elif alignment == "right":
        # half bubble left
        width = 2 * len(spectrum)
        middle = len(spectrum)
    else:
        # Centered bubble
        width = len(spectrum)
        middle = len(spectrum) / 2

    squared_arc = (width / 2) ** 2 - (xaxis - middle) ** 2  # squared half circle
    # squared_arc[squared_arc < 0] = 0
    bubble = np.sqrt(squared_arc) - width
    # find new intersection
    touching_point = (spectrum - bubble).argmin()

    # grow bubble until touching
    bubble = bubble + (spectrum - bubble).min()

    return bubble, touching_point


@njit(cache=True)
def keep_largest(baseline: np.ndarray, bubble: np.ndarray) -> np.ndarray:
    """
    keep_largest selectively updates a baseline region with a bubble, depending
    on which has a greater y-value.

    Usage
    -----
    baseline_ = keep_largest(baseline, bubble)

    Parameters
    ----------
    baseline : np.ndarray
        an input baseline
    bubble : np.ndarray
        an input bubble (usually computed with grow_bubble())

    Returns
    -------
    baseline_ : np.ndarray
        the updated baseline
    """
    for i, _ in enumerate(baseline):
        if baseline[i] < bubble[i]:
            baseline[i] = bubble[i]
    return baseline


def bubbleloop(
    spectrum: np.ndarray, baseline: np.ndarray, min_bubble_widths: list
) -> np.ndarray:
    """
    bubbleloop itteratively updates a baseline estimate by growing bubbles under a spectrum.

    Usage
    -----
    baseline = bubbleloop(spectrum, baseline, min_bubble_widths)

    Parameters
    ----------
    spectrum : np.ndarray
        the input spectrum
    baseline : np.ndarray
        the initial baseline should be akin to np.zeros(spectrum.shape)
    min_bubble_widths : list
        the minimum bubble widths to use. Can be an array-like or int.
        if array-like -> must be the same length as spectrum and baseline. Useful to specify
        different bubble sizes based on x-coordinates.
        if int -> will use the same width for all x-coordinates.

    Returns
    -------
    baseline : np.ndarray
        the updated baseline
    """
    # initial range is always 0 -> len(s). aka the whole spectrum
    # bubblecue is a list of bubble x-coordinate span as
    # [[x0, x2]_0, [x0, x2]_1, ... [x0, x2]_n]
    # additional bubble regions are added as the loop runs.
    range_cue = [[0, len(spectrum)]]

    i = 0
    while i < len(range_cue):
        # Bubble parameter from bubblecue
        left_bound, right_bound = range_cue[i]
        i += 1

        if left_bound == right_bound:
            continue

        if isinstance(min_bubble_widths, int):
            min_bubble_width = min_bubble_widths
        else:
            min_bubble_width = min_bubble_widths[(left_bound + right_bound) // 2]

        if left_bound == 0 and right_bound != (len(spectrum)):
            # half bubble right
            alignment = "left"
        elif left_bound != 0 and right_bound == (len(spectrum)):
            alignment = "right"
            # half bubble left
        else:
            # Reached minimum bubble width
            if (right_bound - left_bound) < min_bubble_width:
                continue
            # centered bubble
            alignment = "center"

        # new bubble
        bubble, relative_touching_point = grow_bubble(
            spectrum[left_bound:right_bound], alignment
        )
        touching_point = relative_touching_point + left_bound

        # add bubble to baseline by keeping largest value
        baseline[left_bound:right_bound] = keep_largest(
            baseline[left_bound:right_bound], bubble
        )
        # Add new bubble(s) to bubblecue
        if touching_point == left_bound:
            range_cue.append([touching_point + 1, right_bound])
        elif touching_point == right_bound:
            range_cue.append([left_bound, touching_point - 1])
        else:
            range_cue.append([left_bound, touching_point])
            range_cue.append([touching_point, right_bound])

    return baseline


def bubblefill_bg(
    spectrum: np.ndarray,
    x_axis: np.ndarray,
    min_bubble_widths: list = 50,
    fit_order: int = 1,
    signal_to_emit: Signal = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    bubblefill splits a spectrum into it's raman and baseline components.

    Usage
    -----
    baseline = bubblefill(spectrum, bubblewidths, fitorder)

    Parameters
    ----------
    spectrum : np.ndarray
        the input spectrum
    min_bubble_widths: list or int
        is the smallest width allowed for bubbles. Smaller values will
        allow bubbles to penetrate further into peaks resulting
        in a more *aggressive* baseline removal. Larger values are more
        *concervative* and might the computed underestimate baseline.
        use list to specify a minimum width that depends on the
        x-coordinate of the bubble. Make sure len(bubblewidths) = len(spectrum).
        Otherwise if bubblewidths [int], the same width is used for all x-coordinates.
    fit_order : int
        the order of the polynomial fit used to remove the *overall* baseline slope.
        Recommendend value is 1 (for linear slope).
        Higher order will result in Runge's phenomena and
        potentially undesirable and unpredictable effects.
        fitorder = 0 is the same as not removing the overall baseline slope

    Returns
    -------
    baseline : np.ndarray
        the spectrum's baseline component

    Reference
    ---------
    Guillaume Sheehy 2021-01
    """

    if signal_to_emit is not None:
        signal_to_emit.emit()

    # Remove general slope
    poly_fit = np.poly1d(np.polyfit(x_axis, spectrum, fit_order))(x_axis)
    spectrum_ = spectrum - poly_fit

    # Normalization
    smin = spectrum_.min()  # value needed to return to the original scaling
    spectrum_ = spectrum_ - smin
    scale = spectrum_.max() / len(spectrum)
    spectrum_ = spectrum_ / scale  # Rescale spectrum to X:Y=1:1 (square aspect ratio)

    baseline = np.zeros(spectrum_.shape)

    # Bubble loop (this is the bulk of the algorithm)
    baseline = bubbleloop(spectrum_, baseline, min_bubble_widths)

    # Bringing baseline back in original scale
    baseline = baseline * scale + poly_fit + smin

    # Final smoothing of baseline (only if bubblewidth is not a list!!!)
    if not isinstance(min_bubble_widths, int):
        filter_width = max(min(min_bubble_widths), 10)
    else:
        filter_width = max(min_bubble_widths, 10)

    baseline = savgol_filter(baseline, int(2 * (filter_width // 4) + 3), 3)

    return baseline


def bubblefill(
    spectral_map: np.ndarray,
    x_axis: np.ndarray,
    min_bubble_widths: list = 50,
    fit_order: int = 1,
    signal_to_emit: Signal = None,
):
    backgrounds = np.apply_along_axis(
        bubblefill_bg,
        2,
        spectral_map,
        x_axis,
        min_bubble_widths,
        fit_order,
        signal_to_emit,
    )
    spectral_map -= backgrounds

    return spectral_map
