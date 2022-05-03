import numpy as np
import scipy.io
import scipy.interpolate as si
import os
from scipy import signal
from functools import reduce
from sklearn import decomposition, cluster
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import scipy.sparse as ss
from scipy.sparse import linalg

import widgets.sklearn_NMF

from PySide6.QtCore import Signal, QSettings

# TODO: Move into different folder -> change structure of the whole app files
class Data:
    """
    A class for raman data representation and methods on it.

    Attributes: # TODO: prepsat sem vsechny atributy
        in_file (str): Matlab file containing the data.
    """

    def __init__(self, in_file: str) -> None:
        """
        The constructor for Data class.
  
        Parameters:
           in_file (str): Matlab file containing the data.  
        """

        self._mdict = {} # dict to save matlab dict into
        self.in_file = in_file
        self.x_axis = None
        self.data = None
        self.maxima = None
        self.averages = None
        self.Z_scores = None
        self.components = []
        self.spikes = {}
        
        self.load_data()

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
            matlab_data = matlab_data[name][0,0]

            # flattened data (individual spectra)
            data = matlab_data[7]

            # num of rows, num of cols
            image_size = tuple(matlab_data[5][0])

            # units = matlab_data[9][1][1]

            self.x_axis = matlab_data[9][1][0][0]

            self.data = np.reshape(data,(image_size[1], image_size[0], -1))

            # maxima for intuitive cosmic rays positions (used in manual removal)
            self.maxima = np.max(self.data, axis=2)
            # averages for spectral map visualization
            self.averages = np.mean(self.data, axis=2)

        except Exception as e:
            raise Exception(f"{self.in_file}: file could not be loaded; {e}")


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
            self._mdict[name][0,0][9][1][0] = [self.x_axis]

            # reshape the data back and set it to its position
            self._mdict[name][0,0][7] = np.reshape(self.data,(self.data.shape[0] * self.data.shape[1], -1), order='C')

            # set spectral map size (may change after cropping)
            self._mdict[name][0,0][5][0] = self.data.shape[:2][::-1]

            scipy.io.savemat(out_file, appendmat=True, mdict=self._mdict)

        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")

    def auto_save_data(self, out_folder: str, file_tag: str) -> None:
        file_name, ext = os.path.basename(self.in_file).split('.')
        out_file = os.path.join(out_folder, file_name + file_tag + '.' + ext)
        
        # do not overwrite on auto save
        if os.path.exists(out_file):
            i = 2
            out_file = os.path.join(out_folder, file_name + file_tag + f"({i})" + '.' + ext)
            while os.path.exists(out_file):
                i += 1
                out_file = os.path.join(out_folder, file_name + file_tag + f"({i})" + '.' + ext)
    
        self.save_data(out_file)

    def _recompute_dependent_data(self) -> None:
        """
        The helper function to recompute the attributes that depend on the self.data attribute.
        """

        self.maxima = np.max(self.data, axis=2) # good for looking at cosmic rays potential positions
        self.averages = np.mean(self.data, axis=2)

    def crop(self, spectra_start: float, spectra_end: float, left: int, top: int, right: int, bottom: int) -> None:
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
        self.x_axis = self.x_axis[x_axis_start:x_axis_end+1]

        # crop the data
        self.data = self.data[left:right, top:bottom, x_axis_start:x_axis_end+1]

        # recompute what depends on self.data because it changed
        self._recompute_dependent_data()

    def auto_crop_absolute(self, spectra_start: float, spectra_end: float):
        # find the closest index into x_axis array to given value on x axis
        x_axis_start = np.argmin(np.abs(self.x_axis - spectra_start))
        x_axis_end = np.argmin(np.abs(self.x_axis - spectra_end))

        # crop the x axis; +1 added because of upper bound is exclusivity
        self.x_axis = self.x_axis[x_axis_start:x_axis_end+1]

        # crop the data
        self.data = self.data[:, :, x_axis_start:x_axis_end+1]

        # NOTE: dependent data are not recomputed here as it is used for visualization only

    def auto_crop_relative(self, spectra_start_crop: int, spectra_end_crop: int):

        try:
            if spectra_end_crop != 0:
                self.x_axis = self.x_axis[spectra_start_crop:-spectra_end_crop]
                self.data = self.data[:, :, spectra_start_crop:-spectra_end_crop]
            else:
                self.x_axis = self.x_axis[spectra_start_crop:]
                self.data = self.data[:, :, spectra_start_crop:]
        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")


        # NOTE: dependent data are not recomputed here as it is used for visualization only

    # linear interpolation between the end-points
    def remove_manual(self, spectrum_index_x: int, spectrum_index_y: int, start: float, end: float) -> None:
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
        self.data[spectrum_index_x, spectrum_index_y, x_axis_start:x_axis_end:1] = new_values

        self._recompute_dependent_data()

    #TODO: to be done - docstrings etc.; move sth to data.func.utils

    def _get_indices_range(self, x, start_value, end_value):
        start_index = np.argmin(np.absolute(x - start_value))
        end_index = np.argmin(np.absolute(x - end_value))
        return np.r_[start_index:end_index]

    def _get_indices_to_fit(self, x, ranges_to_ignore):
        union = reduce(np.union1d, (self._get_indices_range(x, *i) for i in ranges_to_ignore))
        to_fit = np.in1d(np.arange(x.shape[0]), union, invert=True)
        return to_fit

    def _get_no_water_indices(self, x: np.ndarray) -> np.ndarray:
        to_ignore = [[2750, 3750]] # possible C-H vibrations included
        return self._get_indices_to_fit(x, to_ignore)

    def erosion(self, values: np.ndarray, window_width: int) -> np.ndarray:
        # eroze -> minmum v okně
        padded_values = np.pad(values, (window_width, window_width), 'constant', constant_values=(values[0], values[-1])) # pad with side values from sides
        windows = np.lib.stride_tricks.sliding_window_view(padded_values, 2 * window_width + 1)
        mins = np.min(windows, axis=1)
        return mins

    def dilation(self, values: np.ndarray, window_width: int) -> np.ndarray:
        # dilatace -> maximum v okně
        padded_values = np.pad(values, (window_width, window_width), 'constant', constant_values=(values[0], values[-1])) # pad with side values from sides
        windows = np.lib.stride_tricks.sliding_window_view(padded_values, 2 * window_width + 1)
        mins = np.max(windows, axis=1)
        return mins

    def opening(self, values: np.ndarray, window_width: int) -> np.ndarray:
        return self.dilation(self.erosion(values, window_width), window_width)

    def get_optimal_structuring_element_width(self, values: np.ndarray) -> int:
        max_sim_counter = 3
        window_width = 1
        opened_array = self.opening(values, window_width)

        while True:
            window_width += 1
            new_opened_array = self.opening(opened_array, window_width)
            if np.any(new_opened_array != opened_array):
                similarity_counter = 0
                opened_array = new_opened_array
                continue
            else:
                similarity_counter += 1
                if similarity_counter == max_sim_counter:
                    return window_width - max_sim_counter + 1 # restore window width of the first similar result

    #TODO rename
    def _mm_algo_step(self, y, window_width: int = None):
        spectrum_opening = self.opening(y, window_width)
        approximation = np.mean(self.erosion(spectrum_opening, window_width) + self.dilation(spectrum_opening, window_width), axis=0)
        return np.minimum(spectrum_opening, approximation)

    #TODO rename
    def _mm_aaa(self, y: np.ndarray, ignore_water: bool, signal_to_emit: Signal = None) -> np.ndarray:
        if signal_to_emit is not None:
            signal_to_emit.emit()

        if ignore_water:
            water_start_point = 2800
            water_start_index = np.argmin(np.abs(self.x_axis - water_start_point))

            water_part_y = y[water_start_index:]
            not_water_part_y = y[:water_start_index]

            window_width_water = int(np.round(len(water_part_y) / 3)) # TODO: best??
            window_width_no_water = self.get_optimal_structuring_element_width(not_water_part_y)

            bg_water = self._mm_algo_step(water_part_y, window_width_water)
            bg_no_water = self._mm_algo_step(not_water_part_y, window_width_no_water)

            background = np.concatenate((bg_no_water, bg_water))
            return background

        window_width = self.get_optimal_structuring_element_width(y)

        spectrum_opening = self.opening(y, window_width)
        approximation = np.mean(self.erosion(spectrum_opening, window_width) + self.dilation(spectrum_opening, window_width), axis=0)
        background = np.minimum(spectrum_opening, approximation)
        return background

    def mm_algo_spectrum(self, ignore_water: bool, signal_to_emit: Signal = None):
        # no speed-up version - possible speed-ups: multithreading, clustering
        backgrounds = np.apply_along_axis(self._mm_aaa, 2, self.data, ignore_water, signal_to_emit)
        self.data -= backgrounds
        self._recompute_dependent_data()

    def auto_math_morpho(self, ignore_water: bool):
        self.mm_algo_spectrum(ignore_water)

    def vancouver(self, degree: int, ignore_water: bool = True, signal_to_emit: Signal = None):
        backgrounds = np.apply_along_axis(self.vancouver_poly_bg, 2, self.data, degree, ignore_water, signal_to_emit)
        self.data -= backgrounds
        self._recompute_dependent_data()

    def auto_vancouver(self, degree: int, ignore_water: bool) -> None:
        self.vancouver(degree, ignore_water)

    def vancouver_poly_bg(self, y: np.ndarray, degree: int, ignore_water: bool = True, signal_to_emit: Signal = None) -> np.ndarray:
        if signal_to_emit is not None:
            signal_to_emit.emit()

        x = self.x_axis

        if ignore_water:
            no_water_indices = self._get_no_water_indices(x)
            x = x[no_water_indices]
            y = y[no_water_indices]

        signal = y
        first_iter = True
        devs = [0]
        criterium = np.inf

        while criterium > 0.05:
            poly_obj = np.polynomial.Polynomial(None).fit(x, signal, deg=degree)
            poly = poly_obj(x)
            residual = signal - poly
            residual_mean = np.mean(residual)
            DEV = np.sqrt(np.mean((residual - residual_mean)**2))
            devs.append(DEV)
            
            if first_iter: # remove peaks from fitting in first iteration
                not_peak_indices = np.where(signal <= (poly + DEV))
                signal = signal[not_peak_indices]
                x = x[not_peak_indices]
                first_iter = False
            else: # reconstruction
                signal = np.where(signal < poly + DEV, signal, poly + DEV)
            criterium = np.abs((DEV - devs[-2]) / DEV)

        return poly_obj(self.x_axis)

    def poly_bg(self, y: np.ndarray, degree: int, ignore_water: bool = True) -> np.ndarray:
        x = self.x_axis

        if ignore_water:
            no_water_indices = self._get_no_water_indices(x)
            x = x[no_water_indices]
            y = y[no_water_indices]
        
        poly_obj = np.polynomial.Polynomial(None).fit(x, y, deg=degree)
        return poly_obj(self.x_axis)

    def auto_poly(self, degree: int, ignore_water: bool) -> None:
        backgrounds = np.apply_along_axis(self.poly_bg, 2, self.data, degree, ignore_water)
        self.data -= backgrounds
        self._recompute_dependent_data()

    def linearize(self, step: float) -> None:
        spectrum_spline = si.CubicSpline(self.x_axis, self.data, axis=2, extrapolate=False)
        new_x = np.arange(np.ceil(self.x_axis[0]), np.floor(self.x_axis[-1]), step)
        self.x_axis = new_x
        self.data = spectrum_spline(new_x)

        self._recompute_dependent_data()

    def auto_linearize(self, step: float) -> None:
        self.linearize(step)

    # decomposition methods

    def PCA(self, n_components: int) -> None:
        self.components = [] # reset to init state

        # TODO: abs?
        reshaped_data = np.reshape(np.abs(self.data), (-1, self.data.shape[2]))
        pca = decomposition.PCA(n_components=n_components) #TODO: mozna nejaka regularizace apod.
        pca.fit(reshaped_data)
        pca_transformed_data = pca.transform(reshaped_data)

        for i in range(len(pca.components_)):
            self.components.append({"map": pca_transformed_data[:,i].reshape(self.data.shape[0], self.data.shape[1]), "plot": pca.components_[i]})

    def auto_PCA(self, n_components: int) -> None:
        self.PCA(n_components)

    def NMF(self, n_components: int, signal_to_emit: Signal = None) -> None:
        self.components = [] # reset to init state

        # np.abs has to be present since NMF requires positive values

        """
        # sub min to make non-negative
        temp_data = self.data - np.repeat(np.min(self.data, axis=2)[:,:,np.newaxis], self.data.shape[2], 2)
        reshaped_data = np.reshape(temp_data, (-1, self.data.shape[2]))
        """

        #abs
        reshaped_data = np.reshape(np.abs(self.data), (-1, self.data.shape[2]))
        nmf = widgets.sklearn_NMF.NMF(n_components=n_components, init="nndsvd", signal_to_emit=signal_to_emit) # TODO: mozna nejaka regularizace apod.
        nmf.fit(reshaped_data)
        nmf_transformed_data = nmf.transform(reshaped_data)

        for i in range(len(nmf.components_)):
            self.components.append({"map": nmf_transformed_data[:,i].reshape(self.data.shape[0], self.data.shape[1]), "plot": nmf.components_[i]})

    def auto_NMF(self, n_components: int) -> None:
        self.NMF(n_components)

    def export_components(self, file_name: str, file_format: str) -> None:
        # matplotlib pic export
        n_components = len(self.components)

        # app settings
        settings = QSettings()

        # letters for components identification
        comp_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        # reverse ([::-1]) -> want the best components on the top and plotting happens from the bottom
        component_plots = [component["plot"] for component in self.components][::-1]
        component_maps = [component["map"] for component in self.components][::-1]

        plt.figure(figsize=(14, n_components * 2.5))

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
            plt.axis('off')
            # set limist so that frame can be made
            ax.set_xlim(-1.5, self.data.shape[0] + 1.5)
            ax.set_ylim(-1.5, self.data.shape[1] + 1.5)

            # frame with color corresponding to plot's one
            rec = patches.Rectangle((-1.5, -1.5), self.data.shape[0] + 3, self.data.shape[1] + 3, linewidth=2, edgecolor=colors[n_components -1 - i], facecolor=colors[n_components - 1 - i])
            rec.set_zorder(0)
            ax.add_patch(rec)

            # need to plot starting from the last image so that position fits with plot
            plt.imshow(component_maps[n_components - 1 - i].reshape(self.data.shape[0], self.data.shape[1]).T, extent=[0, self.data.shape[0], 0, self.data.shape[1]], cmap=cmap)
            
            # move to next row
            index += n_cols

        # plots

        # shifts for annotation and lines so that they can be on top of each other in one plot
        shift_step = np.max(component_plots) + 3

        letter_shift_x = -150
        letter_shift_y = -5
        annotaion_shift_y = 0.6
        annotation_shift_x = - 0.015 * len(self.x_axis)
        shift = 0

        plt.subplot(n_components, 2, (2, 2 * n_components))
        # set ylim so that upper plot has same space above as other plots
        plt.ylim(top=shift_step * n_components, bottom=-1)
        plt.xlim(self.x_axis[0], self.x_axis[-1])
        plt.axis('on')

        for i in range(n_components):
            plt.plot(self.x_axis, component_plots[i] + shift, linewidth=2, color=colors[i])

            # find and annotate important peaks
            peaks, _ = signal.find_peaks(component_plots[i], prominence=0.8, distance=20)
            for peak_index in peaks:
                plt.annotate(f"{int(np.round(self.x_axis[peak_index]))}", (self.x_axis[peak_index] + annotation_shift_x, component_plots[i][peak_index] + shift + annotaion_shift_y), ha='left', rotation=90)

            # letter annotation
            plt.annotate(comp_letters[n_components - 1 - i], (self.x_axis[-1] + letter_shift_x, (i + 1)*shift_step + letter_shift_y), size="xx-large", weight="bold")
            # component_plots[i][-1]
            shift += shift_step

        # reduce space between maps and plots
        # plt.subplots_adjust(wspace=-0.2, hspace=0.1)
        

        plt.xlabel("Raman shift (cm$^{-1}$)")
        plt.ylabel("Intensity (a.u.)")
        plt.yticks([])
        
        plt.tight_layout()
        plt.savefig(file_name, bbox_inches='tight', format=file_format)

    def auto_export(self, out_folder: str, file_tag: str, file_format: str):
        file_name, _ = os.path.basename(self.in_file).split('.')
        out_file = os.path.join(out_folder, file_name + file_tag + '.' + file_format)

        # do not overwrite on auto export
        if os.path.exists(out_file):
            i = 2
            out_file = os.path.join(out_folder, file_name + file_tag + f"({i})" + '.' + file_format)
            while os.path.exists(out_file):
                i += 1
                out_file = os.path.join(out_folder, file_name + file_tag + f"({i})" + '.' + file_format)

        self.export_components(out_file, file_format)

    def _calculate_Z_scores(self, data: np.ndarray) -> np.ndarray:
        abs_differences = np.abs(np.diff(data, axis=1))
        percentile_90 = np.percentile(abs_differences, 90)
        deviation = np.median(np.abs(abs_differences - percentile_90))
        Z = 0.6745 * (abs_differences - percentile_90) / deviation
        return Z

    def calculate_spikes_indices(self):
        Z_score_threshold = 6.5
        window_width = 5
        n_comp = 8
        correlation_threshold = 0.9
        silent_region = [1900, 2600]

        clf = cluster.MiniBatchKMeans(n_clusters=n_comp, random_state=42, max_iter=60)
        # flatten data and ingore silent region
        flattened_data = np.reshape(self.data, (-1, self.data.shape[-1]))[:,self._get_indices_to_fit(self.x_axis, [silent_region])]
        clf.fit(flattened_data)
        cluster_map = np.reshape(clf.predict(flattened_data), self.data.shape[:2])

        comps = {}
        zets = {}
        map_indices = []
        peak_positions = []

        for i in range(n_comp):
            comps[i] = np.asarray(np.where(cluster_map == i)).T
            zets[i] = self._calculate_Z_scores(self.data[comps[i][:, 0], comps[i][:, 1], :])
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
                spike_window_end = np.minimum(spike_position + window_width + 1, self.data.shape[2])
                spike_rel_index = np.argmax(curr_spectrum[spike_window_start : spike_window_end])
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
                if position[1] == self.data.shape[1] - 1: # lower border
                    ref_spectrum = self.data[position[0], position[1] - 1, :]
                elif position[1] == 0: # upper border
                    ref_spectrum = self.data[position[0], position[1] + 1, :]
                else: # OK
                    spectrum_above = self.data[position[0], position[1] - 1, :]
                    spectrum_below = self.data[position[0], position[1] + 1, :]
                    ref_spectrum = (spectrum_above + spectrum_below) / 2

                left = int(np.maximum(spike_position - window_width, 0))
                # right can be `self.data.shape[2]` as it is used for slicing only
                right = int(np.minimum(spike_position + window_width + 1, self.data.shape[2]))

                curr_spec_window = curr_spectrum[left : right]
                ref_spec_window = ref_spectrum[left : right]

                corr = np.corrcoef(curr_spec_window, ref_spec_window)[0, -1]
                if corr < correlation_threshold:
                    map_indices.append(position)
                    peak_positions.append(spike_position)

        self.spikes["map_indices"] = map_indices
        self.spikes["peak_positions"] = peak_positions

    def remove_spikes(self) -> None:
        # NOTE: remove spikes before cropping!

        window_width = 5
        for spectrum_indices, spike_position in zip(self.spikes["map_indices"], self.spikes["peak_positions"]):
            curr_spectrum = self.data[spectrum_indices[0], spectrum_indices[1], :]

            # NOTE: right cannot be data.data.shape[2] as it's for indexing as well
            left = int(np.maximum(spike_position - window_width, 0))
            right = int(np.minimum(spike_position + window_width + 1, len(curr_spectrum) - 1))

            # use median when "normal" value is not obtainable (extreme indices)
            median = np.median(curr_spectrum)

            start_value = curr_spectrum[left] if left > 0 else median
            end_value = curr_spectrum[right] if right < len(curr_spectrum) - 1 else median

            values_count = right - left 
            new_values = np.linspace(start_value, end_value, num=values_count + 1)

            self.data[spectrum_indices[0], spectrum_indices[1], left:right+1:1] = new_values

        self._recompute_dependent_data()

    def auto_remove_spikes(self):
        self.calculate_spikes_indices()
        self.remove_spikes()

    '''
    whittaker_smooth, airPLS:

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
    '''

    def whittaker_smooth(self, x, w, lambda_, differences=1):
        '''
        Penalized least squares algorithm for background fitting
        
        input
            x: input data (i.e. chromatogram of spectrum)
            w: binary masks (value of the mask is zero if a point belongs to peaks and one otherwise)
            lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background
            differences: integer indicating the order of the difference of penalties
        
        output
            the fitted background vector
        '''

        X = np.matrix(x)
        m = X.size
        E = ss.eye(m,format='csc')
        for _ in range(differences):
            E = E[1:]-E[:-1]
        W = ss.diags(w, 0, shape=(m, m))
        A = ss.csc_matrix(W + (lambda_ * E.T *E))
        B = ss.csc_matrix(W * X.T)
        background = linalg.spsolve(A, B)
        return np.array(background)

    #TODO: nechat uzivatele lambdu nastavit? 
    def airPLS(self, x, lambda_=10**4.4, porder=1, itermax=20):
        '''
        Adaptive iteratively reweighted penalized least squares for baseline fitting
        
        input
            x: input data (i.e. chromatogram of spectrum)
            lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background, z
            porder: adaptive iteratively reweighted penalized least squares for baseline fitting
        
        output
            the fitted background vector
        '''

        m = x.shape[0]
        w = np.ones(m)
        for i in range(1,itermax+1):
            z = self.whittaker_smooth(x, w, lambda_, porder)
            d = x-z
            dssn = np.abs(d[d<0].sum())
            if (dssn < 0.001*(abs(x)).sum() or i==itermax):
                break
            # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
            w[d>=0] = 0
            w[d<0] = np.exp(i*np.abs(d[d<0])/dssn)
            w[0] = np.exp(i*(d[d<0]).max()/dssn)
            w[-1] = w[0]
        return z

    def auto_airPLS(self):
        backgrounds = np.apply_along_axis(self.airPLS, 2, self.data)
        self.data -= backgrounds
        self._recompute_dependent_data()