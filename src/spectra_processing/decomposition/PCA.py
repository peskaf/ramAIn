import numpy as np
from sklearn import decomposition


def PCA(spectral_map: np.ndarray, n_components: int) -> list:
    """
    A function to perform simple PCA method on the spectral map.

    Parameters:
        n_components (int): Number of component to be estimated.
    """

    components = []

    reshaped_data = np.reshape(spectral_map, (-1, spectral_map.shape[2]))
    pca = decomposition.PCA(n_components=n_components)
    pca_transformed_data = pca.fit_transform(reshaped_data)
    print(pca.components_)
    for i, component in enumerate(pca.components_):
        components.append(
            {
                "map": pca_transformed_data[:, i].reshape(
                    spectral_map.shape[0], spectral_map.shape[1]
                ),
                "plot": component,
            }
        )
    return components
