import numpy as np
from sklearn.cluster import KMeans

# NOTE: NEW ALGORITHM
# On preprocessed data - that means cropped, CR removed, BG removed, smoothed
# 1. Crop the data to the C-H band (2830-3030 cm-1)
# 2. Cluster the data into 20 clusters
# 3. For each cluster, calculate mean of the cropped spectra that fall into it
# 4. Select the cluster with the lowest mean as the one containing the best water candidates
# 5. Average the spectra in the best cluster to get the average water spectrum in our spectral map


def _get_average_water(data: np.ndarray, x_axis: np.ndarray):
    N = 30

    cluster_data = data.reshape(-1, data.shape[-1])
    c_h_band = (x_axis > 2830) & (x_axis < 3030)
    cluster_data = cluster_data[:, c_h_band]  # just band of C-H vibrations

    kmeans = KMeans(n_clusters=N, random_state=0).fit(cluster_data)

    # create array of cluster data divided by cluster label - so label 0 are on row 0, label 1 on row 1 etc.
    cluster_data = np.array(
        [cluster_data[kmeans.labels_ == i].mean(axis=0) for i in range(N)]
    )

    means = np.mean(cluster_data, axis=1)
    id_lowest = np.argmin(means)

    # get indices of spectra in cluster woth lowest mean
    idx_lowest = np.where(kmeans.labels_ == id_lowest)[0]
    water_candidates = data.reshape(-1, data.shape[-1])[idx_lowest]
    mean_water = water_candidates.mean(axis=0)

    water_spectra_mask = np.where(kmeans.labels_ == id_lowest, 1, 0).reshape(
        data.shape[:-1]
    )

    return mean_water, water_spectra_mask


def water_normalization(
    spectral_map: np.ndarray,
    x_axis: np.ndarray,
    average_water: np.ndarray,
) -> np.ndarray:

    WATER_BAND = (2800, 3800)
    NORMALIZED_INTEGRAL_VALUE = 100000

    # NOTE: Jana P. (21.2.2022, 22:41): integrate signal between 2800 and 3800 cm-1
    # NOTE: Sarka (pdf manual sent by Peter 23. 2. 2022, 14:51): integrate the area of valence vibrations of water  and find normalization factor so that this integral is equal 100000. Multiply the spectral map by this normalization factor.
    # TODO: check with Peter

    # Normalization itself
    start_index = np.where(x_axis >= WATER_BAND[0])[0][0]
    end_index = np.where(x_axis <= WATER_BAND[1])[0][-1]
    water_band = average_water[start_index:end_index]
    water_band_integral = np.trapz(water_band, x_axis[start_index:end_index])

    normalization_factor = NORMALIZED_INTEGRAL_VALUE / water_band_integral
    normalized_spectral_map = spectral_map * normalization_factor

    return normalized_spectral_map
