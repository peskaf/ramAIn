import numpy as np
import scipy.interpolate as si
from numpy.linalg import norm


# On preprocessed data - that means cropped, CR removed, BG removed, smoothed (if not, we smooth it here to find the best water, TODO: try)
# 1. Preprocess pure water spectrum - interpolate it to the same x axis as the data (align the x axes)
# 2. Calculate differences between the spectra to get rid of the different heights
# 3. Calculate cosine similarity between the water and the data
# 4. Find the best matches based on the threshold
# 5. Average the best matches to get the average water spectrum from our data
# 6. Use this average water spectrum for normalization of the data
#
# Things to think about:
# - What is the best threshold for the cosine similarity?
# - What is the best way to average the best matches? Do we do some weighting based on the similarity?
# - What to do if we do not find any good matches?


def _load_reference_spectrum() -> tuple[list, list]:
    """
    Load the reference spectrum for water normalization.

    Returns
    -------
    x_axis_water : list
        The x-axis of the reference spectrum.
    values_water : list
        The values of the reference spectrum.
    """
    # Load pure water
    x_axis_water = []
    values_water = []

    # TODO: insert normal pure water instead of sea water
    with open("src/resources/reference_spectra/sea_water_mean.txt") as pure_spectrum:
        for line in pure_spectrum:
            x, val = line.split()
            x_axis_water.append(float(x))
            values_water.append(float(val))
    return x_axis_water, values_water


def _calculate_differences(spectra):
    differences = np.array([np.diff(spectrum) for spectrum in spectra])
    return differences


def _cosine_similarity(a, b):
    if a.shape != b.shape:
        raise ValueError("The shapes of both arrays must be the same.")

    # Compute the norms of each row
    norms_a = norm(a, axis=1)
    norms_b = norm(b, axis=1)

    # Compute the dot product of corresponding rows
    dot_product = np.sum(a * b, axis=1)

    # Calculate cosine similarity
    similarities = dot_product / (norms_a * norms_b)

    return similarities


def _get_average_water(
    distances: np.ndarray, data: np.ndarray, distance_threshold: float
):
    reshaped_data = data.reshape((-1, data.shape[-1]))
    water_spectra_mask = np.where(
        np.abs(distances) <= distance_threshold, 1, 0
    ).reshape(data.shape[:-1])

    if np.sum(water_spectra_mask) == 0:
        return None, water_spectra_mask

    average_water = np.mean(
        reshaped_data[np.abs(distances) <= distance_threshold], axis=0
    )
    return average_water, water_spectra_mask


def _get_cosine_distances(spectral_map: np.ndarray, x_axis: np.ndarray):
    data = spectral_map.reshape((-1, spectral_map.shape[-1]))

    # Load reference spectrum
    x_axis_water, values_water = _load_reference_spectrum()

    # Interpolate the pure water and get values in the datapoints we had in the original data (berofe detrending)
    # Align the water spectrum with the input spectrum
    spectrum_spline = si.CubicSpline(
        x_axis_water, values_water, axis=2, extrapolate=False
    )
    aligned_values_water = spectrum_spline(x_axis)

    # Find the index of the first and the last non-NaN value
    nans = np.where(~np.isnan(aligned_values_water))[0]
    first_non_nan_index = nans[0]
    last_non_nan_index = nans[-1]

    x_axis = x_axis[first_non_nan_index : last_non_nan_index + 1]
    aligned_values_water = aligned_values_water[
        first_non_nan_index : last_non_nan_index + 1
    ]
    data = data[:, first_non_nan_index : last_non_nan_index + 1]

    # Calculate the differences so that we get rid of the different height of the spectra
    differences_spectra = _calculate_differences(data)
    differences_water = _calculate_differences(aligned_values_water.reshape((1, -1)))
    distances = 1 - _cosine_similarity(
        np.tile(differences_water[0], [differences_spectra.shape[0], 1]),
        differences_spectra,
    )  # NOTE:  1 - to get a distance

    return distances


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
