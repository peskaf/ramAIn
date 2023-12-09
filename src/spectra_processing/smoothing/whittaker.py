from scipy import sparse
import numpy as np


def whittaker(spectral_map: np.ndarray, lam: int = 1600, diff: int = 2) -> np.ndarray:
    spectral_map_ = spectral_map.view((-1, spectral_map.shape[2]))
    if spectral_map_.ndim != 2:
        raise ValueError("Input must be a 2D array")

    num_spectra, L = spectral_map_.shape
    E = sparse.csc_matrix(np.diff(np.eye(L), diff))
    W = sparse.spdiags(np.ones(L), 0, L, L)
    Z = W + lam * E.dot(E.transpose())

    # Pre-factorize Z for efficiency
    Z_inv = sparse.linalg.factorized(Z)

    # Solve for each spectrum (each row in Y)
    smoothed_data = np.array([Z_inv(spectral_map_[i, :]) for i in range(num_spectra)])
    smoothed_data = smoothed_data.reshape(spectral_map.shape)

    return smoothed_data
