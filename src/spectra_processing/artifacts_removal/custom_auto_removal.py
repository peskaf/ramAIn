import numpy as np
from sklearn import cluster
from typing import List, Tuple

from ...utils import indices


def _calculate_mmZ_scores(spectral_map: np.ndarray) -> np.ndarray:
    """
    A function to calculate modified modified Z (mmZ) scores of the spectra.
    Note that modified is written twice in previous sentence as it is in fact
    modification of modified Z score.

    Paramaters:
        data (np.ndarray): Data on which to calculate the modified modified Z scores.
    """

    # detrend the data
    abs_differences = np.abs(np.diff(spectral_map, axis=1))
    # use 90th percentile instead of the median
    percentile_90 = np.percentile(abs_differences, 90)
    # deviation will still be medain
    deviation = np.median(np.abs(abs_differences - percentile_90))
    # multiplication constant stays the same as in modified Z score as the algorithm is optimized to it
    mmZ = 0.6745 * (abs_differences - percentile_90) / deviation

    return mmZ


def calculate_spikes_indices(
    spectral_map: np.ndarray, x_axis: np.ndarray
) -> Tuple[List, List]:
    """
    A function to calculate spikes positions in spectral map and in spectral plot using newly developed algorithm.
    """

    # modified modified Z score threshold -> lower thresholds removes also bigger noise
    Z_score_threshold = 6.5  # prev: 5.5

    # window widht for spike deletion and spike alignment
    window_width = 5

    # components for clustering
    n_comp = 8

    # correlation threshold for correlation filter
    correlation_threshold = 0.9

    # silent region of the data to be ignored during clustering
    silent_region = [1900, 2600]

    clf = cluster.MiniBatchKMeans(
        n_clusters=n_comp, random_state=42, max_iter=60, n_init="auto"
    )

    # flatten data and ingore silent region
    flattened_data = np.reshape(spectral_map, (-1, spectral_map.shape[-1]))[
        :, indices.get_indices_to_fit(x_axis, [silent_region])
    ]
    clf.fit(flattened_data)
    cluster_map = np.reshape(clf.predict(flattened_data), spectral_map.shape[:2])

    comps = {}
    zets = {}
    map_indices = []
    peak_positions = []

    for i in range(n_comp):
        comps[i] = np.asarray(np.where(cluster_map == i)).T
        zets[i] = _calculate_mmZ_scores(spectral_map[comps[i][:, 0], comps[i][:, 1], :])
        spectrum, spike_pos = np.where(zets[i] > Z_score_threshold)
        pos = comps[i][spectrum]

        # no spike detected -> next iteration
        if len(pos) < 1:
            continue

        # align spike tops
        spike_tops = []
        for position, spike_position in zip(pos, spike_pos):
            curr_spectrum = spectral_map[position[0], position[1], :]
            spike_window_start = np.maximum(spike_position - window_width, 0)
            spike_window_end = np.minimum(
                spike_position + window_width + 1, spectral_map.shape[2]
            )
            spike_rel_index = np.argmax(
                curr_spectrum[spike_window_start:spike_window_end]
            )
            spike_top = spike_window_start + spike_rel_index
            spike_tops.append(spike_top)

        # keep only unique entries
        stacked = np.unique(np.column_stack((pos, spike_tops)), axis=0)
        pos = stacked[:, :2]
        spike_tops = stacked[:, 2]

        # covariance filtering
        for position, spike_position in zip(pos, spike_tops):
            curr_spectrum = spectral_map[position[0], position[1], :]

            # get reference spectrum
            if position[1] == spectral_map.shape[1] - 1:  # lower border
                ref_spectrum = spectral_map[position[0], position[1] - 1, :]
            elif position[1] == 0:  # upper border
                ref_spectrum = spectral_map[position[0], position[1] + 1, :]
            else:  # OK
                spectrum_above = spectral_map[position[0], position[1] - 1, :]
                spectrum_below = spectral_map[position[0], position[1] + 1, :]
                ref_spectrum = (spectrum_above + spectrum_below) / 2

            left = int(np.maximum(spike_position - window_width, 0))
            # right can be `sspectral_map.shape[2]` as it is used for slicing only
            right = int(
                np.minimum(spike_position + window_width + 1, spectral_map.shape[2])
            )

            curr_spec_window = curr_spectrum[left:right]
            ref_spec_window = ref_spectrum[left:right]

            corr = np.corrcoef(curr_spec_window, ref_spec_window)[0, -1]
            if corr < correlation_threshold:
                map_indices.append(position)
                peak_positions.append(spike_position)

    return map_indices, peak_positions


def remove_spikes(
    spectral_map: np.ndarray, spike_indices: np.ndarray, peak_positions: np.ndarray
) -> None:
    """
    A function to remove estimated spikes from the data using newly developed algorithm.

    NOTE: spikes should be removed before cropping because artificial values may be added to the end
    or to the beginning.
    """

    # window widgt for spikes removal
    window_width = 5

    for spectrum_indices, spike_position in zip(spike_indices, peak_positions):
        curr_spectrum = spectral_map[spectrum_indices[0], spectrum_indices[1], :]

        # NOTE: right cannot be data.data.shape[2] as it's for indexing as well
        left = int(np.maximum(spike_position - window_width, 0))
        right = int(
            np.minimum(spike_position + window_width + 1, len(curr_spectrum) - 1)
        )

        # values to linearly interpolate
        # place the other bound if value would be part of spike (else branches)
        start_value = curr_spectrum[left] if left > 0 else curr_spectrum[right]
        end_value = (
            curr_spectrum[right]
            if right < len(curr_spectrum) - 1
            else curr_spectrum[left]
        )

        values_count = right - left

        # create linear interpolation
        new_values = np.linspace(start_value, end_value, num=values_count + 1)

        # replace values
        spectral_map[
            spectrum_indices[0], spectrum_indices[1], left : right + 1 : 1
        ] = new_values

    return spectral_map
