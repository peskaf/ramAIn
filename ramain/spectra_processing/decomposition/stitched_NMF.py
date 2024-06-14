import numpy as np
from ramain.spectra_processing.decomposition.sklearn_NMF import NMF as sklearn_NMF
from PySide6.QtCore import Signal


def stitched_NMF(
    spectral_maps: list, n_components: int, signal_to_emit: Signal = None
) -> list:
    """
    A function to perform NMF method on the spectral map with NNDSVD initialization,
    that is initialization based on SVD/PCA for better estimation.
    Note that NMF method is local check point from sklear implementation.

    Parameters:
        n_components (int): Number of component to be estimated.
        signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.
    """

    x_axes = [sm.x_axis for sm in spectral_maps]
    dataset = [sm.data for sm in spectral_maps]

    # Unify the x axis for all spectra
    min_x = np.max([x[0] for x in x_axes])
    max_x = np.min([x[-1] for x in x_axes])

    # get average step size in x axes
    mean_step_size = np.mean([np.mean(np.diff(x_axis)) for x_axis in x_axes])

    # interpolate each spectrum and get values for the new common x axis
    new_x_axis = np.arange(min_x, max_x, mean_step_size)
    new_dataset = []
    for i, (x_axis, data) in enumerate(zip(x_axes, dataset)):
        new_data = np.zeros((data.shape[0], data.shape[1], len(new_x_axis)))
        for j in range(data.shape[0]):
            for k in range(data.shape[1]):
                new_data[j, k] = np.interp(new_x_axis, x_axis, data[j, k])
        new_dataset.append(new_data)

    # stitch
    dataset = new_dataset
    data = np.concatenate(
        [data.reshape((-1, data.shape[-1])) for data in dataset], axis=0
    )

    reshaped_data = np.abs(data.reshape((-1, data.shape[-1])))

    init = "nndsvd"
    max_iter = 200

    nmf = sklearn_NMF(
        n_components=n_components,
        init=init,
        max_iter=max_iter,
        signal_to_emit=signal_to_emit,
    )

    nmf_transformed_data = nmf.fit_transform(reshaped_data)

    return nmf_transformed_data, nmf.components_, new_x_axis
