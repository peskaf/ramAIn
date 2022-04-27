import numpy as np
import scipy.io
import scipy.interpolate as si
from scipy import signal
from functools import reduce
from sklearn import decomposition
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from PySide6.QtCore import Signal

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
        self.x_axis = None
        self.data = None
        self.maxima = None
        self.averages = None
        self.Z_scores = None
        self.components = []
        
        self.load_data(in_file)

    def load_data(self, in_file: str) -> None:
        """
        The function to load the data from file with given name.

        Parameters:
            in_file (str): Matlab file containing the data.  
        """

        # load .mat data with expected structure
        matlab_data = scipy.io.loadmat(in_file, mdict=self._mdict)

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

    def save_data(self, out_file: str) -> None:
        """
        The function to save the data to file with given name.

        Parameters:
            out_file (str): Matlab file that is to be created.  
        """

        # add .mat if it's not present (app won't find other extensions)
        if not out_file.endswith(".mat"):
            out_file = out_file + ".mat"

        # m_dict is not empty -> some data was loaded
        if self._mdict:
            # keep the structure of input file (as in load_data)

            # name of the data structure
            name = list(self._mdict)[-1] 

            # set x axis values
            self._mdict[name][0,0][9][1][0] = [self.x_axis]

            # reshape the data back and set it to its position
            self._mdict[name][0,0][7] = np.reshape(self.data,(self.data.shape[0] * self.data.shape[1], -1), order='C')

            # set spectral map size (may change after cropping)
            self._mdict[name][0,0][5][0] = self.data.shape[:2][::-1]

            scipy.io.savemat(out_file, mdict=self._mdict)

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

    def _calculate_Z_scores(self) -> None:
        """
        The function to calculate the modified Z-scores for the data.
        """

        # "detrend" the data
        diff = np.diff(self.data, axis=2)

        # median of each spectrum
        M = np.median(diff, axis=2)

        # widen the median to `diff` dimension for vectorized computation
        wide_M = np.repeat(M[:,:,np.newaxis], diff.shape[2], 2)

        # median absolute deviation of each spectrum
        MAD = np.median(np.abs(diff-wide_M), axis=2)

        # calculate the modified Z scores and save it in the attribute as it will be reused frequently
        self.Z_scores = 0.6745 * (diff - wide_M) / np.repeat(MAD[:,:,np.newaxis], diff.shape[2], 2)

    def get_spikes_positions(self, threshold: float) -> np.ndarray:
        """
        The function to get indices of the spikes according to the given threshold.

        Parameters:
            threshold (float): Value on which to separate valid and invalid data.

        Returns:
            spikes_positions (np.ndarray): Array of indices of spectra containing spikes in a spectral map.
        """

        if self.Z_scores is None:
            self._calculate_Z_scores()

        spikes_positions = np.unique(np.vstack(np.where(np.abs(self.Z_scores) > threshold)[:2]).T, axis=0)

        return spikes_positions

    def remove_spikes(self, threshold: float, window_width: int) -> None: # TODO: zkusit nahradit nejen ty spiky (data s 0) ale celé okno okolo těchto spiků!
        """
        The function to remove the spikes using the sliding-window-filter.

        Note that the `window_width` must be large enough so that some valid signal falls into it (typically at least 4).
        Parameters:
            threshold (float): Value on which to separate valid and invalid data.
            window_width (int): Width of the sliding window; it's size is then 2 * window_width + 1.
        """

        #TODO: pokud je kono moc male, aby tam bylo neco validniho, vlozi se misto celeho spektra "NaN", vyresit! (zdetsit okno na minimum z nejmensiho mozneho a zadaneho uzivatelem)

        # add first Z value (was not computed as we "detrended" the data) so that it exceeds the threshold automatically (in case it has spike)
        new_Z = np.insert(self.Z_scores, [0], np.full((self.Z_scores.shape[0], self.Z_scores.shape[1], 1), threshold + 1), axis=2)
        # make the last Z-score to exceed the threshold as well in case CR appears there -> sliding window would not restore it properly
        new_Z[:,:,-1] = threshold + 1

        # get mask for the convolution (0 .. spike is present, 1 .. spike is not present)
        window_mask = np.less_equal(np.abs(new_Z), np.full(new_Z.shape, threshold)).astype(np.float64)
        # pad with zeros for preservation of the size of the input after convolution
        window_mask_padded = np.pad(window_mask, ((0,0), (0,0), (window_width, window_width)))

        # counts how many ones are in each window (i.e. values that are below threshold)
        divisors = np.apply_along_axis(np.convolve, 2, window_mask_padded, np.ones(2 * window_width + 1), 'valid')

        # replaces invalid data with 0 ->kernel of all ones can be used everywhere
        masked_data = self.data * window_mask

        # pad with zeros for preservation of the size of the input after convolution
        masked_data_padded = np.pad(masked_data, ((0,0), (0,0), (window_width, window_width)))
        convolved_data = np.apply_along_axis(np.convolve, 2, masked_data_padded, np.ones(2 * window_width + 1), 'valid')

        # divide each intensity by the number of non_zero values it was computed from in the convolution
        restored_data = convolved_data / divisors

        # replace only spikes with restored data values -> assigning restored data everywhere
        # would cause smoothing of the data which is not desirable
        self.data = np.where(masked_data > 0, self.data, restored_data)

        self._recompute_dependent_data()
    
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
        to_ignore = [[2950, 3750]]
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

    def vancouver(self, degree: int, ignore_water: bool = True, signal_to_emit: Signal = None):
        backgrounds = np.apply_along_axis(self.vancouver_poly_bg, 2, self.data, degree, ignore_water, signal_to_emit)
        self.data -= backgrounds
        self._recompute_dependent_data()

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

    def linearize(self, step: float) -> None:
        spectrum_spline = si.CubicSpline(self.x_axis, self.data, axis=2, extrapolate=False)
        new_x = np.arange(np.ceil(self.x_axis[0]), np.floor(self.x_axis[-1]), step)
        self.x_axis = new_x
        self.data = spectrum_spline(new_x)
        self._recompute_dependent_data()

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

    def NMF(self, n_components: int) -> None:
        self.components = [] # reset to init state

        # np.abs has to be present since NMF requires positive values
        reshaped_data = np.reshape(np.abs(self.data), (-1, self.data.shape[2]))
        nmf = decomposition.NMF(n_components=n_components, init="nndsvd") #TODO: mozna nejaka regularizace apod.
        nmf.fit(reshaped_data)
        nmf_transformed_data = nmf.transform(reshaped_data)

        for i in range(len(nmf.components_)):
            self.components.append({"map": nmf_transformed_data[:,i].reshape(self.data.shape[0], self.data.shape[1]), "plot": nmf.components_[i]})

    def export_components(self, file_name: str, file_format: str, components_names: list[str]=None) -> None:
        # matplotlib pic export
        n_components = len(self.components)

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
            plt.imshow(component_maps[n_components - 1 - i].reshape(self.data.shape[0], self.data.shape[1]).T, extent=[0, self.data.shape[0], 0, self.data.shape[1]])
            
            # move to next row
            index += n_cols

        # plots

        # shifts for annotation and lines so that they can be on top of each other in one plot
        shift_step = np.max(component_plots) + 3

        letter_shift_x = -150
        letter_shift_y = 3
        annotaion_shift_y = 0.6
        annotation_shift_x = - 0.015 * len(self.x_axis)
        shift = 0

        plt.subplot(5, 2, (2, 10))
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
            plt.annotate(comp_letters[n_components - 1 - i], (self.x_axis[-1] + letter_shift_x, component_plots[i][-1] + shift + letter_shift_y), size="xx-large", weight="bold")

            shift += shift_step

        # reduce space between maps and plots
        plt.subplots_adjust(wspace=-0.2, hspace=0.1)
        

        plt.xlabel("Raman shift (cm$^{-1}$)")
        plt.ylabel("Intensity (a.u.)")
        plt.yticks([])
        
        plt.tight_layout()
        plt.savefig(file_name, bbox_inches='tight', format=file_format)