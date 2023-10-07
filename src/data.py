import numpy as np
import os
from sklearn import decomposition, cluster
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import scipy.io
import scipy.interpolate as si
import scipy.sparse as ss
from scipy import signal
from scipy.sparse import linalg

from PySide6.QtCore import Signal, QSettings

import src.spectra_processing.decomposition.sklearn_NMF
import utils.indices
import utils.math_morphology

import warnings

warnings.filterwarnings("ignore")


class Data:
    """
    A class for raman data representation and methods on it.
    """

    def __init__(self, in_file: str) -> None:
        """
        The constructor for Data class representing Raman spectral map to be processed
        with methods availible on this class' instance.

        Parameters:
           in_file (str): Matlab file containing the data.
        """

        self._mdict = {}  # dict to save matlab dict into
        self.in_file = in_file
        self.x_axis = None
        self.data = None
        self.maxima = None
        self.averages = None
        self.Z_scores = None
        self.components = []
        self.spikes = {}

        self.load_data()

    # DONE
    def load_data(self) -> None:
        """
        The function to load the data from `self.in_file`.
        """
        try:
            # load .mat data with expected structure
            matlab_data = scipy.io.loadmat(self.in_file, mdict=self._mdict)

            # extract relevant information
            # last one is the name of the data structure
            name = list(self._mdict)[-1]
            matlab_data = matlab_data[name][0, 0]

            # flattened data (individual spectra)
            data = matlab_data[7]

            # num of rows, num of cols
            image_size = tuple(matlab_data[5][0])

            # units = matlab_data[9][1][1]

            self.x_axis = matlab_data[9][1][0][0]

            self.data = np.reshape(data, (image_size[1], image_size[0], -1))

            # TEST
            # from scipy.signal import savgol_filter
            # self.data = np.apply_along_axis(savgol_filter, 2, self.data, 5, 2)
            # TEST END

            # maxima for intuitive cosmic rays positions (used in manual removal)
            self.maxima = np.max(self.data, axis=2)
            # averages for spectral map visualization
            self.averages = np.mean(self.data, axis=2)

        except Exception as e:
            raise Exception(f"{self.in_file}: file could not be loaded; {e}")

    # DONE
    def save_data(self, out_file: str) -> None:
        """
        The function to save the data to file with given name.

        Parameters:
            out_file (str): Matlab file that is to be created.
        """

        try:
            # keep the structure of input file (as in load_data)

            # name of the data structure
            name = list(self._mdict)[-1]

            # set x axis values
            self._mdict[name][0, 0][9][1][0] = [self.x_axis]

            # reshape the data back and set it to its position
            self._mdict[name][0, 0][7] = np.reshape(
                self.data, (self.data.shape[0] * self.data.shape[1], -1), order="C"
            )

            # set spectral map size (may change after cropping)
            self._mdict[name][0, 0][5][0] = self.data.shape[:2][::-1]

            scipy.io.savemat(out_file, appendmat=True, mdict=self._mdict)

        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")

    # DONE
    def auto_save_data(self, out_folder: str, file_tag: str) -> None:
        """
        A function for automatic data saving.

        Parameters:
            out_folder (str): Folder where to store the data.
            file_tag (str): String to append to the `self.in_file` name.
        """

        # create resulting file name
        file_name, ext = os.path.basename(self.in_file).split(".")
        out_file = os.path.join(out_folder, file_name + file_tag + "." + ext)

        # do not overwrite on auto save -> append ('number') to the name instead
        if os.path.exists(out_file):
            i = 2
            out_file = os.path.join(
                out_folder, file_name + file_tag + f"({i})" + "." + ext
            )
            while os.path.exists(out_file):
                i += 1
                out_file = os.path.join(
                    out_folder, file_name + file_tag + f"({i})" + "." + ext
                )

        self.save_data(out_file)

    def _recompute_dependent_data(self) -> None:
        """
        The helper function to recompute the attributes that depend on the self.data attribute.
        """

        self.maxima = np.max(
            self.data, axis=2
        )  # good for looking at cosmic rays potential positions
        self.averages = np.mean(self.data, axis=2)

    # DONE
    def crop(
        self,
        spectra_start: float,
        spectra_end: float,
        left: int,
        top: int,
        right: int,
        bottom: int,
    ) -> None:
        """
        The function to crop the data according to given parameters.

        Parameters:
            spectra_start (float): Value on x axis from which to start cropping the spectra.
            spectra_end (float): Value on x axis where to end cropping the spectra.
            left (int): The left-most index from which to crop the spectral map (upper left corner x).
            top (int): The top-most index from which to crop the spectral map (upper left corner y).
            right (int): The right-most index to which to crop the spectral map (lower right corner x).
            bottom (int): The bottom-most index to which to crop the spectral map (lower right corner y).
        """

        # find the closest index into x_axis array to given value on x axis
        x_axis_start = np.argmin(np.abs(self.x_axis - spectra_start))
        x_axis_end = np.argmin(np.abs(self.x_axis - spectra_end))

        # crop the x axis; +1 added because of upper bound is exclusivity
        self.x_axis = self.x_axis[x_axis_start : x_axis_end + 1]

        # crop the data
        self.data = self.data[left:right, top:bottom, x_axis_start : x_axis_end + 1]

        # recompute what depends on self.data because it changed
        self._recompute_dependent_data()

    # DONE
    def auto_crop_absolute(self, spectra_start: float, spectra_end: float) -> None:
        """
        A function for absolute automatic data cropping.
        Absolute means that specific values for x axis are provided.

        Parameters:
            spectra_start (float): Value from which to crop the data.
            spectra_end (float): Value to which to crop the data.
        """

        try:
            # find the closest index into x_axis array to given value on x axis
            x_axis_start = np.argmin(np.abs(self.x_axis - spectra_start))
            x_axis_end = np.argmin(np.abs(self.x_axis - spectra_end))

            # crop the x axis; +1 added because of upper bound is exclusivity
            self.x_axis = self.x_axis[x_axis_start : x_axis_end + 1]

            # crop the data
            self.data = self.data[:, :, x_axis_start : x_axis_end + 1]

        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")

    # DONE
    def auto_crop_relative(
        self, spectra_start_crop: int, spectra_end_crop: int
    ) -> None:
        """
        A function for relative automatic data cropping.
        Relative means that relative units to be cropped from each of the sides are provided,
        e.g. spectra_start_crop = 50 -> crop first 50 values (datapoints) from the data.

        Parameters:
            spectra_start_crop (int): Value from which to crop the data.
            spectra_end_crop (int): Value to which to crop the data.
        """

        # NOTE: user may provide indices that result in empty array, this is OK for cropping,
        #       exception will be raised somewhere else

        try:
            if spectra_end_crop != 0:
                self.x_axis = self.x_axis[spectra_start_crop:-spectra_end_crop]
                self.data = self.data[:, :, spectra_start_crop:-spectra_end_crop]
            else:
                self.x_axis = self.x_axis[spectra_start_crop:]
                self.data = self.data[:, :, spectra_start_crop:]

        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")

    # DONE
    def remove_manual(
        self, spectrum_index_x: int, spectrum_index_y: int, start: float, end: float
    ) -> None:
        """
        The function to remove spike using linear interpolation of the end-points in the given spectrum.

        Parameters:
            spectrum_index_x (int): Index x of the spectrum in the spectral map where the removal takes place.
            spectrum_index_y (int): Index y of the spectrum in the spectral map where the removal takes place.
            start (float): Value on x axis from which to start the interpolation of the spectra.
            end (float): Value on x axis where to end the interpolation of the spectra.
        """

        # get corresponding indices into x_axis array
        x_axis_start = np.argmin(np.abs(self.x_axis - start))
        x_axis_end = np.argmin(np.abs(self.x_axis - end))

        # get end-points of the interpolation
        start_value = self.data[spectrum_index_x, spectrum_index_y, x_axis_start]
        end_value = self.data[spectrum_index_x, spectrum_index_y, x_axis_end]

        # how many values there are betweent the end-points
        values_count = x_axis_end - x_axis_start

        # interpolation
        new_values = np.linspace(start_value, end_value, num=values_count)
        self.data[
            spectrum_index_x, spectrum_index_y, x_axis_start:x_axis_end:1
        ] = new_values

        self._recompute_dependent_data()

    # DONE
    def _calculate_Z_scores(self, data: np.ndarray) -> np.ndarray:
        """
        A function to calculate modified modified Z scores of the spectra.
        Note that modified is written twice in previous sentence as it is in fact
        modification of modified Z score.

        Paramaters:
            data (np.ndarray): Data on which to calculate the modified modified Z scores.
        """

        # detrend the data
        abs_differences = np.abs(np.diff(data, axis=1))
        # use 90th percentile instead of the median
        percentile_90 = np.percentile(abs_differences, 90)
        # deviation will still be medain
        deviation = np.median(np.abs(abs_differences - percentile_90))
        # multiplication constant stays the same as in modified Z score as the algorithm is optimalized to it
        Z = 0.6745 * (abs_differences - percentile_90) / deviation
        return Z

    # DONE
    def calculate_spikes_indices(self) -> None:
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

        clf = cluster.MiniBatchKMeans(n_clusters=n_comp, random_state=42, max_iter=60)

        # flatten data and ingore silent region
        flattened_data = np.reshape(self.data, (-1, self.data.shape[-1]))[
            :, utils.indices.get_indices_to_fit(self.x_axis, [silent_region])
        ]
        clf.fit(flattened_data)
        cluster_map = np.reshape(clf.predict(flattened_data), self.data.shape[:2])

        comps = {}
        zets = {}
        map_indices = []
        peak_positions = []

        for i in range(n_comp):
            comps[i] = np.asarray(np.where(cluster_map == i)).T
            zets[i] = self._calculate_Z_scores(
                self.data[comps[i][:, 0], comps[i][:, 1], :]
            )
            spectrum, spike_pos = np.where(zets[i] > Z_score_threshold)
            pos = comps[i][spectrum]

            # no spike detected -> next iteration
            if len(pos) < 1:
                continue

            # align spike tops
            spike_tops = []
            for position, spike_position in zip(pos, spike_pos):
                curr_spectrum = self.data[position[0], position[1], :]
                spike_window_start = np.maximum(spike_position - window_width, 0)
                spike_window_end = np.minimum(
                    spike_position + window_width + 1, self.data.shape[2]
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
                curr_spectrum = self.data[position[0], position[1], :]

                # get reference spectrum
                if position[1] == self.data.shape[1] - 1:  # lower border
                    ref_spectrum = self.data[position[0], position[1] - 1, :]
                elif position[1] == 0:  # upper border
                    ref_spectrum = self.data[position[0], position[1] + 1, :]
                else:  # OK
                    spectrum_above = self.data[position[0], position[1] - 1, :]
                    spectrum_below = self.data[position[0], position[1] + 1, :]
                    ref_spectrum = (spectrum_above + spectrum_below) / 2

                left = int(np.maximum(spike_position - window_width, 0))
                # right can be `self.data.shape[2]` as it is used for slicing only
                right = int(
                    np.minimum(spike_position + window_width + 1, self.data.shape[2])
                )

                curr_spec_window = curr_spectrum[left:right]
                ref_spec_window = ref_spectrum[left:right]

                corr = np.corrcoef(curr_spec_window, ref_spec_window)[0, -1]
                if corr < correlation_threshold:
                    map_indices.append(position)
                    peak_positions.append(spike_position)

        # store the indices so that it does not have to be computed again
        self.spikes["map_indices"] = map_indices
        self.spikes["peak_positions"] = peak_positions

    # DONE
    def remove_spikes(self) -> None:
        """
        A function to remove estimated spikes from the data using newly developed algorithm.

        NOTE: spikes should be removed before cropping because artificial values may be added to the end
        or to the beginning.
        """

        # window widgt for spikes removal
        window_width = 5

        for spectrum_indices, spike_position in zip(
            self.spikes["map_indices"], self.spikes["peak_positions"]
        ):
            curr_spectrum = self.data[spectrum_indices[0], spectrum_indices[1], :]

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
            self.data[
                spectrum_indices[0], spectrum_indices[1], left : right + 1 : 1
            ] = new_values

        self._recompute_dependent_data()

    # DONE
    def get_optimal_structuring_element_width(self, values: np.ndarray) -> int:
        """
        A function to compute optimal structuring element for the math morphology bg removal approach.
        Implementation of algorithm by Perez-Pueyo et al (doi: 10.1366/000370210791414281).

        Parameters:
            values (np.ndarray): Values for which to compute the optimal structuring elementd width.

        Returns:
            window_width (int): Optimal structuring element width.
        """

        # how many similar results have to occure to end the algorithm
        max_sim_counter = 3

        window_width = 1
        opened_array = utils.math_morphology.opening(values, window_width)

        while True:
            window_width += 1
            new_opened_array = utils.math_morphology.opening(opened_array, window_width)
            if np.any(new_opened_array != opened_array):
                similarity_counter = 0
                opened_array = new_opened_array
                continue
            else:
                similarity_counter += 1
                if similarity_counter == max_sim_counter:
                    return (
                        window_width - max_sim_counter + 1
                    )  # restore window width of the first similar result

    # DONE
    def _math_morpho_step(self, y: np.ndarray, window_width: int) -> np.ndarray:
        """
        One step of the math morpho bg subtraction algorithm.
        Implementation of algorithm by Perez-Pueyo et al (doi: 10.1366/000370210791414281).

        Parameters:
            y (np.ndarray): Values on which mathematical morphology methods are performed.
            window_width (int): Width of the structuring element for MM operations.

        Returns:
            result (np.ndarray): Values after one step of the alogrithm.
        """

        spectrum_opening = utils.math_morphology.opening(y, window_width)
        approximation = np.mean(
            utils.math_morphology.erosion(spectrum_opening, window_width)
            + utils.math_morphology.dilation(spectrum_opening, window_width),
            axis=0,
        )
        return np.minimum(spectrum_opening, approximation)

    # DONE
    def _math_morpho_on_spectrum(
        self, y: np.ndarray, ignore_water: bool, signal_to_emit: Signal = None
    ) -> np.ndarray:
        """
        A function to perform math morpho algorithm on one spectrum, icluding water ignorance and signal emiting.
        Implementation of changed algorithm by Perez-Pueyo et al (doi: 10.1366/000370210791414281).

        Parameters:
            y (np.ndarray): Spectrum on which the algorithm will be performed.
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
            signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.

        Returns:
            result (np.ndarray): Estimated background of the provided spectrum `y`.
        """

        if signal_to_emit is not None:
            signal_to_emit.emit()

        if ignore_water:
            water_start_point = 2800
            water_start_index = np.argmin(np.abs(self.x_axis - water_start_point))

            water_part_y = y[water_start_index:]
            not_water_part_y = y[:water_start_index]

            window_width_water = int(np.round(len(water_part_y) / 3))  # TODO: best??
            window_width_no_water = self.get_optimal_structuring_element_width(
                not_water_part_y
            )

            bg_water = self._math_morpho_step(water_part_y, window_width_water)
            bg_no_water = self._math_morpho_step(
                not_water_part_y, window_width_no_water
            )

            background = np.concatenate((bg_no_water, bg_water))
            return background

        window_width = self.get_optimal_structuring_element_width(y)

        spectrum_opening = utils.math_morphology.opening(y, window_width)
        approximation = np.mean(
            utils.math_morphology.erosion(spectrum_opening, window_width)
            + utils.math_morphology.dilation(spectrum_opening, window_width),
            axis=0,
        )
        background = np.minimum(spectrum_opening, approximation)
        return background

    # DONE
    def math_morpho(self, ignore_water: bool, signal_to_emit: Signal = None) -> None:
        """
        No speed-up version of the math morpho bg subtraction algorithm Perez-Pueyo et al (doi: 10.1366/000370210791414281)
        with version for water ignorance. Algorithm is performed on all spectra in the spectral map.

        Possible speed-ups: clustering for optimal structuring element estimation, multithreading.

        Parameters:
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
            signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.
        """

        backgrounds = np.apply_along_axis(
            self._math_morpho_on_spectrum, 2, self.data, ignore_water, signal_to_emit
        )
        self.data -= backgrounds
        self._recompute_dependent_data()

    # DONE
    def auto_math_morpho(self, ignore_water: bool) -> None:
        """
        A function to perform automatic math morpho bg subtraction on the spectral map.

        Parameters:
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
        """

        self.math_morpho(ignore_water)

    # DONE
    def imodpoly_poly_bg(
        self,
        y: np.ndarray,
        degree: int,
        ignore_water: bool = True,
        signal_to_emit: Signal = None,
    ) -> np.ndarray:
        """
        Implementation of I-ModPoly algorithm for bg subtraction (Zhao et al, doi: 10.1366/000370207782597003), added vaersion
        with possible water ignorance and signal emission.

        Parameters:
            y (np.ndarray): Spectrum on which the algorithm will be performed.
            degree (int): Degree of the polynomial used for interpolation.
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed. Default: True.
            signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.

        Returns:
            result (np.ndarray): Estimated background of the provided spectrum `y`.
        """

        if signal_to_emit is not None:
            signal_to_emit.emit()

        x = self.x_axis

        # ignore indices of water
        if ignore_water:
            no_water_indices = utils.indices.get_no_water_indices(x)
            x = x[no_water_indices]
            y = y[no_water_indices]

        signal = y
        first_iter = True
        devs = [0]
        criterium = np.inf

        # algorithm based on the article
        while criterium > 0.05:
            poly_obj = np.polynomial.Polynomial(None).fit(x, signal, deg=degree)
            poly = poly_obj(x)
            residual = signal - poly
            residual_mean = np.mean(residual)
            DEV = np.sqrt(np.mean((residual - residual_mean) ** 2))
            devs.append(DEV)

            if first_iter:  # remove peaks from fitting in first iteration
                not_peak_indices = np.where(signal <= (poly + DEV))
                signal = signal[not_peak_indices]
                x = x[not_peak_indices]
                first_iter = False
            else:  # reconstruction
                signal = np.where(signal < poly + DEV, signal, poly + DEV)
            criterium = np.abs((DEV - devs[-2]) / DEV)

        # NOTE: ploynomial has to be evaluated at every point of `self.x_axis` here as it is background for the whole spectrum
        return poly_obj(self.x_axis)

    # DONE
    def imodpoly(
        self, degree: int, ignore_water: bool = True, signal_to_emit: Signal = None
    ) -> None:
        """
        A function that applies the I-ModPoly algorithm on the whole spectral map. Zhao et al (doi: 10.1366/000370207782597003)

        Parameters:
            degree (int): Degree of the polynomial used for interpolation.
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed. Default: True.
            signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.
        """

        backgrounds = np.apply_along_axis(
            self.imodpoly_poly_bg, 2, self.data, degree, ignore_water, signal_to_emit
        )
        self.data -= backgrounds
        self._recompute_dependent_data()

    # DONE
    def auto_imodpoly(self, degree: int, ignore_water: bool) -> None:
        """
        A function to perform I-ModPoly algorithm in auto processing.

        Parameters:
            degree (int): Degree of the polynomial used for interpolation.
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
        """

        self.imodpoly(degree, ignore_water)

    # DONE
    def poly_bg(
        self, y: np.ndarray, degree: int, ignore_water: bool = True
    ) -> np.ndarray:
        """
        A function to perform simple polynomial interpolation on the spectrum to estimate the backgrounds.
        Water can be ingored.

        Parameters:
            y (np.ndarray): Spectrum on which the algorithm will be performed.
            degree (int): Degree of the polynomial used for interpolation.
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed. Default: True.

        Returns:
            result (np.ndarray): Estimated background of the provided spectrum `y`.
        """
        x = self.x_axis

        if ignore_water:
            no_water_indices = utils.indices.get_no_water_indices(x)
            x = x[no_water_indices]
            y = y[no_water_indices]

        poly_obj = np.polynomial.Polynomial(None).fit(x, y, deg=degree)
        # NOTE: ploynomial has to be evaluated at every point of `self.x_axis` here as it is background for the whole spectrum
        return poly_obj(self.x_axis)

    # DONE
    def auto_poly(self, degree: int, ignore_water: bool) -> None:
        """
        A function to perform polynomial background estimation and subtraction on the whole
        spectral map.

        Parameters:
            degree (int): Degree of the polynomial used for interpolation.
            ignore_water (bool): Info whether variation of the algo with water ignorace should be performed.
        """

        backgrounds = np.apply_along_axis(
            self.poly_bg, 2, self.data, degree, ignore_water
        )
        self.data -= backgrounds
        self._recompute_dependent_data()

    # DONE
    def linearize(self, step: float) -> None:
        """
        A function to perform data linearization on the whole spectral map.
        That means that there will be equal steps between the data points.

        Parameters:
            step (float): Required step between the data points.
        """

        spectrum_spline = si.CubicSpline(
            self.x_axis, self.data, axis=2, extrapolate=False
        )
        new_x = np.arange(np.ceil(self.x_axis[0]), np.floor(self.x_axis[-1]), step)
        self.x_axis = new_x
        self.data = spectrum_spline(new_x)

        self._recompute_dependent_data()

    # DONE
    def auto_linearize(self, step: float) -> None:
        """
        A function to perform linearization on auto processing.

        Parameters:
            step (float): Required step between the data points.
        """

        self.linearize(step)

    # decomposition methods

    # DONE
    def PCA(self, n_components: int) -> None:
        """
        A function to perform simple PCA method on the spectral map.

        Parameters:
            n_components (int): Number of component to be estimated.
        """

        self.components = []  # reset to init state

        reshaped_data = np.reshape(self.data, (-1, self.data.shape[2]))
        pca = decomposition.PCA(n_components=n_components)
        pca.fit(reshaped_data)
        pca_transformed_data = pca.transform(reshaped_data)

        for i in range(len(pca.components_)):
            self.components.append(
                {
                    "map": pca_transformed_data[:, i].reshape(
                        self.data.shape[0], self.data.shape[1]
                    ),
                    "plot": pca.components_[i],
                }
            )

    # DONE
    def auto_PCA(self, n_components: int) -> None:
        """
        A function to perform PCA on auto processing.

        Parameters:
            n_components (int): Number of component to be estimated.
        """

        self.PCA(n_components)

    # DONE
    def NMF(self, n_components: int, signal_to_emit: Signal = None) -> None:
        """
        A function to perform NMF method on the spectral map with NNDSVD initialization,
        that is initialization based on SVD/PCA for better estimation.
        Note that NMF method is local check point from sklear implementation.

        Parameters:
            n_components (int): Number of component to be estimated.
            signal_to_emit (PySide6.QtCore.Signal): Signal to emit while executing the algorithm. Default: None.
        """

        self.components = []  # reset to init state

        init = "nndsvd"
        max_iter = 200

        # NOTE: version with min subtraction instead of making the values absolute -> performed bad
        #       currently not used but may be after some more testing
        # sub min to make non-negative
        # temp_data = self.data - np.repeat(np.min(self.data, axis=2)[:,:,np.newaxis], self.data.shape[2], 2)
        # reshaped_data = np.reshape(temp_data, (-1, self.data.shape[2]))

        # np.abs has to be present since NMF requires non-negative values (sometimes even positive)
        reshaped_data = np.reshape(np.abs(self.data), (-1, self.data.shape[2]))
        # NOTE: some regularization or max_iter may be changed for better performance
        nmf = src.spectra_processing.decomposition.sklearn_NMF.NMF(
            n_components=n_components,
            init=init,
            max_iter=max_iter,
            signal_to_emit=signal_to_emit,
        )  # l1_ratio
        nmf.fit(reshaped_data)
        nmf_transformed_data = nmf.transform(reshaped_data)

        for i in range(len(nmf.components_)):
            self.components.append(
                {
                    "map": nmf_transformed_data[:, i].reshape(
                        self.data.shape[0], self.data.shape[1]
                    ),
                    "plot": nmf.components_[i],
                }
            )

    # DONE
    def auto_NMF(self, n_components: int) -> None:
        """
        A function to perform NMF on auto processing.

        Parameters:
            n_components (int): Number of component to be estimated.
        """

        self.NMF(n_components)

    # DONE
    def export_components_txt(self, file_name: str) -> None:
        """
        A function for components exporting into txt files.

        Parameters:
            file_name (str): Name of the file where the output should be stored.
        """

        SEP = "\t"
        components_rows = np.array([component["plot"] for component in self.components])
        components_columns = components_rows.T
        data_columns = np.concatenate(
            (self.x_axis[:, np.newaxis], components_columns), axis=1
        )

        with open(file_name, "w+") as f:
            for row in data_columns:
                for column in row:
                    f.write(f"{column:.7e}")
                    f.write(SEP)
                f.write("\n")

    # DONE
    def export_components_graphics(self, file_name: str, file_format: str) -> None:
        """
        A function for components exporting for publications.

        Parameters:
            file_name (str): Name of the file where the output should be stored.
            file_format (str): Format of the output, possible formats: png, pdf, ps, eps, svg.
        """
        # matplotlib pic export
        n_components = len(self.components)

        # app settings
        settings = QSettings()

        # letters for components identification
        comp_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

        # reverse ([::-1]) -> want the best components on the top and plotting happens from the bottom
        component_plots = [component["plot"] for component in self.components][::-1]
        component_maps = [component["map"] for component in self.components][::-1]

        plt.figure(figsize=(14, n_components * 2.5), clear=True)

        # set white background on exported images
        plt.rcParams["savefig.facecolor"] = "white"

        # colors for matplotlib plotting
        colors = list(mcolors.TABLEAU_COLORS)
        cmap = str(settings.value("spectral_map/cmap"))
        # subplot params
        n_rows = len(component_plots)
        n_cols = 2
        index = 1

        # maps
        for i in range(n_components):
            ax = plt.subplot(n_rows, n_cols, index)
            plt.axis("off")
            # set limist so that frame can be made
            ax.set_xlim(-1.5, self.data.shape[0] + 1.5)
            ax.set_ylim(-1.5, self.data.shape[1] + 1.5)

            # frame with color corresponding to plot's one
            rec = patches.Rectangle(
                (-1.5, -1.5),
                self.data.shape[0] + 3,
                self.data.shape[1] + 3,
                linewidth=2,
                edgecolor=colors[n_components - 1 - i],
                facecolor=colors[n_components - 1 - i],
            )
            rec.set_zorder(0)
            ax.add_patch(rec)

            # need to plot starting from the last image so that position fits with plot
            plt.imshow(
                component_maps[n_components - 1 - i]
                .reshape(self.data.shape[0], self.data.shape[1])
                .T,
                extent=[0, self.data.shape[0], 0, self.data.shape[1]],
                cmap=cmap,
            )

            # move to next row
            index += n_cols

        # plots

        # shifts for annotation and lines so that they can be on top of each other in one plot
        shift_step = np.max(component_plots) + 3

        letter_shift_x = -150
        letter_shift_y = -5
        annotaion_shift_y = 0.6
        annotation_shift_x = -0.015 * len(self.x_axis)
        shift = 0

        plt.subplot(n_components, 2, (2, 2 * n_components))

        # set ylim so that upper plot has same space above as other plots
        plt.ylim(top=shift_step * n_components, bottom=-1)
        plt.xlim(self.x_axis[0], self.x_axis[-1])
        plt.axis("on")

        for i in range(n_components):
            plt.plot(
                self.x_axis, component_plots[i] + shift, linewidth=2, color=colors[i]
            )

            # find and annotate important peaks
            peaks, _ = signal.find_peaks(
                component_plots[i], prominence=0.8, distance=20
            )
            for peak_index in peaks:
                plt.annotate(
                    f"{int(np.round(self.x_axis[peak_index]))}",
                    (
                        self.x_axis[peak_index] + annotation_shift_x,
                        component_plots[i][peak_index] + shift + annotaion_shift_y,
                    ),
                    ha="left",
                    rotation=90,
                )

            # letter annotation
            plt.annotate(
                comp_letters[n_components - 1 - i],
                (
                    self.x_axis[-1] + letter_shift_x,
                    (i + 1) * shift_step + letter_shift_y,
                ),
                size="xx-large",
                weight="bold",
            )
            shift += shift_step

        # reduce space between maps and plots
        # plt.subplots_adjust(wspace=-0.2, hspace=0.1)

        plt.xlabel("Raman shift (cm$^{-1}$)")
        plt.ylabel("Intensity (a.u.)")
        plt.yticks([])

        plt.tight_layout()
        plt.savefig(file_name, bbox_inches="tight", format=file_format)
        # close the figure as this may not run in the main thread
        plt.close()

    # DONE
    def auto_export_graphics(
        self, out_folder: str, file_tag: str, file_format: str
    ) -> None:
        """
        A function for exporting graphics in automatic pipeline.

        Parameters:
            out_folder (str): Folder where the exported file will be stored.
            file_tag (str): String to append to the `self.in_file` name.
            file_format (str): Format of the output, possible formats: png, pdf, ps, eps, svg.
        """

        if len(self.components) == 0:
            raise Exception("components have not been made yet.")

        # construct the file name
        file_name, _ = os.path.basename(self.in_file).split(".")
        out_file = os.path.join(out_folder, file_name + file_tag + "." + file_format)

        # do not overwrite on auto export -> apend ('number') to the file name instead
        if os.path.exists(out_file):
            i = 2
            out_file = os.path.join(
                out_folder, file_name + file_tag + f"({i})" + "." + file_format
            )
            while os.path.exists(out_file):
                i += 1
                out_file = os.path.join(
                    out_folder, file_name + file_tag + f"({i})" + "." + file_format
                )

        self.export_components_graphics(out_file, file_format)

    # DONE
    def auto_export_txt(self, out_folder: str, file_tag: str) -> None:
        """
        A function for exporting txt components in automatic pipeline.

        Parameters:
            out_folder (str): Folder where the exported file will be stored.
            file_tag (str): String to append to the `self.in_file` name.
        """

        if len(self.components) == 0:
            raise Exception("components have not been made yet.")

        # construct the file name
        file_format = "txt"
        file_name, _ = os.path.basename(self.in_file).split(".")
        out_file = os.path.join(out_folder, file_name + file_tag + "." + file_format)

        # do not overwrite on auto export -> apend ('number') to the file name instead
        if os.path.exists(out_file):
            i = 2
            out_file = os.path.join(
                out_folder, file_name + file_tag + f"({i})" + "." + file_format
            )
            while os.path.exists(out_file):
                i += 1
                out_file = os.path.join(
                    out_folder, file_name + file_tag + f"({i})" + "." + file_format
                )

        self.export_components_txt(out_file)

    # DONE
    def auto_remove_spikes(self) -> None:
        """
        A function for automatic spikes removal.
        """

        self.calculate_spikes_indices()
        self.remove_spikes()

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

    # DONE
    def whittaker_smooth(
        self, x: np.ndarray, w: np.ndarray, lambda_: int, differences: int = 1
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

        X = np.matrix(x)
        m = X.size
        E = ss.eye(m, format="csc")

        for _ in range(differences):
            E = E[1:] - E[:-1]

        W = ss.diags(w, 0, shape=(m, m))
        A = ss.csc_matrix(W + (lambda_ * E.T * E))
        B = ss.csc_matrix(W * X.T)

        background = linalg.spsolve(A, B)
        return np.array(background)

    # DONE
    def airPLS(
        self, x: np.ndarray, lambda_: int = 10**4, porder: int = 1, itermax: int = 20
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
            z = self.whittaker_smooth(x, w, lambda_, porder)
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

    # DONE
    def auto_airPLS(self, lambda_) -> None:
        """
        A function to perform airPLS algorithm on the whole spectral map in the auto processing module.
        """

        backgrounds = np.apply_along_axis(self.airPLS, 2, self.data, lambda_)
        self.data -= backgrounds
        self._recompute_dependent_data()
