import numpy as np
from .sklearn_NMF import NMF as sklearn_NMF
from PySide6.QtCore import Signal


def NMF(
    spectral_map: np.ndarray, n_components: int, signal_to_emit: Signal = None
) -> list:
    """
    A function to perform NMF method on the spectral map with NNDSVD initialization,
    that is initialization based on SVD/PCA for better estimation.
    Note that NMF method is local check point from sklear implementation.

    Parameters:
        n_components (int): Number of component to be estimated.
        signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.
    """

    components = []

    init = "nndsvd"
    max_iter = 200

    # np.abs has to be present since NMF requires non-negative values (sometimes even positive)
    reshaped_data = np.reshape(np.abs(spectral_map), (-1, spectral_map.shape[2]))

    # NOTE: some regularization or max_iter may be changed for better performance
    nmf = sklearn_NMF(
        n_components=n_components,
        init=init,
        max_iter=max_iter,
        signal_to_emit=signal_to_emit,
    )  # l1_ratio
    nmf_transformed_data = nmf.fit_transform(reshaped_data)

    for i, component in enumerate(nmf.components_):
        components.append(
            {
                "map": nmf_transformed_data[:, i].reshape(
                    spectral_map.shape[0], spectral_map.shape[1]
                ),
                "plot": component,
            }
        )

    return components
