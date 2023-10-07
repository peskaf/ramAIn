"""
- whittaker_smooth and airPLS were implemented by someone else:

Source: https://raw.githubusercontent.com/zmzhang/airPLS/master/airPLS.py

airPLS.py Copyright 2014 Renato Lombardo - renato.lombardo@unipa.it
Baseline correction using adaptive iteratively reweighted penalized least squares

This program is a translation in python of the R source code of airPLS version 2.0
by Yizeng Liang and Zhang Zhimin - https://code.google.com/p/airpls
Reference:
Z.-M. Zhang, S. Chen, and Y.-Z. Liang, Baseline correction using adaptive iteratively reweighted penalized least squares. Analyst 135 (5), 1138-1146 (2010).

Description from the original documentation:

Baseline drift always blurs or even swamps signals and deteriorates analytical results, particularly in multivariate analysis.  It is necessary to correct baseline drift to perform further data analysis. Simple or modified polynomial fitting has been found to be effective in some extent. However, this method requires user intervention and prone to variability especially in low signal-to-noise ratio environments. The proposed adaptive iteratively reweighted Penalized Least Squares (airPLS) algorithm doesn't require any user intervention and prior information, such as detected peaks. It iteratively changes weights of sum squares errors (SSE) between the fitted baseline and original signals, and the weights of SSE are obtained adaptively using between previously fitted baseline and original signals. This baseline estimator is general, fast and flexible in fitting baseline.

LICENCE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import numpy as np
import scipy.sparse as ss
from scipy.sparse import linalg


def airPLS(spectral_map: np.ndarray, lambda_: int) -> None:
    """
    A function to perform airPLS algorithm on the whole spectral map in the auto processing module.
    """

    backgrounds = np.apply_along_axis(airPLS_spectrum, 2, spectral_map, lambda_)
    spectral_map -= backgrounds
    return spectral_map


def airPLS_spectrum(
    x: np.ndarray, lambda_: int = 10**4, porder: int = 1, itermax: int = 20
) -> np.ndarray:
    """
    Adaptive iteratively reweighted penalized least squares for baseline fitting.

    Parameters:
        x (np.ndarray): Input data (i.e. chromatogram of spectrum).
        lambda_ (int): Parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background. Default: 10**4.4.
        porder (int): Adaptive iteratively reweighted penalized least squares for baseline fitting. Default: 1.
        itermax (int): Maximum iterations. Default: 20.

    Returns:
        result (np.ndarray): The fitted background vector.
    """

    m = x.shape[0]
    w = np.ones(m)
    for i in range(1, itermax + 1):
        z = whittaker_smooth(x, w, lambda_, porder)
        d = x - z
        dssn = np.abs(d[d < 0].sum())

        if dssn < 0.001 * (abs(x)).sum() or i == itermax:
            break

        # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
        w[d >= 0] = 0
        w[d < 0] = np.exp(i * np.abs(d[d < 0]) / dssn)
        w[0] = np.exp(i * (d[d < 0]).max() / dssn)
        w[-1] = w[0]

    return z


# NOTE: adjusted not to use `np.matrix`
def whittaker_smooth(
    x: np.ndarray, w: np.ndarray, lambda_: int, differences: int = 1
) -> np.ndarray:
    """ "
    Penalized least squares algorithm for background fitting.

    Parameters:
        x (np.ndarray): Input data (i.e. chromatogram of spectrum).
        w (np.ndarray): Binary masks (value of the mask is zero if a point belongs to peaks and one otherwise).
        lambda_ (int): Parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background.
        differences (int): Integer indicating the order of the difference of penalties.

    Returns:
        result (np.ndarray): The fitted background vector.
    """

    X = x.reshape((1, -1))
    m = X.size
    E = ss.eye(m, format="csc")

    for _ in range(differences):
        E = E[1:] - E[:-1]

    W = ss.diags(w, 0, shape=(m, m))
    A = ss.csc_matrix(W + (lambda_ * E.T * E))
    B = ss.csc_matrix(W * X.T)

    background = linalg.spsolve(A, B)
    return np.array(background)
