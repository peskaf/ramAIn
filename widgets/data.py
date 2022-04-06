import numpy as np
import scipy.io

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
        
        self.load_data(in_file)

    def load_data(self, in_file: str) -> None:
        """
        The function to load the data from file with given name.

        Parameters:
            in_file (str): Matlab file containing the data.  
        """

        # load only .mat data with expected structure
        try:
            # load matlab
            matlab_data = scipy.io.loadmat(in_file, mdict=self._mdict)

            # extract relevant information
            # last one is the name of the data structure
            name = list(self._mdict)[-1]
            matlab_data = matlab_data[name][0,0]

            # flattened data (individual spectra)
            data = matlab_data[7]

            # TODO: data before reshaping -> only for current method testing
            self.pure_data = data

            # num of rows, num of cols
            image_size = tuple(matlab_data[5][0]) 

            # units = matlab_data[9][1][1]

            self.x_axis = matlab_data[9][1][0][0]
            self.data = np.reshape(data,(image_size[1], image_size[0], -1))

            # maxima for intuitive cosmic rays positions (used in manual removal)
            self.maxima = np.max(self.data, axis=2)
            # averages for spectral map visualization
            self.averages = np.mean(self.data, axis=2)
        except:
            print("Invalid file format or structure.")

    def save_data(self, out_file: str) -> None:
        """
        The function to save the data to file with given name.

        Parameters:
            out_file (str): Matlab file that is to be created.  
        """

        # add .mat if it's not present (app won't find other extentions)
        if not out_file.endswith(".mat"):
            out_file = out_file + ".mat"

        # m_dict is not empty -> some data was loaded
        if self._mdict:
            # keep the structure of input file (as in load_data)

            # name of the data structure
            name = list(self._mdict)[-1] 

            # set x axis values
            self._mdict[name][0,0][9][1][0][0] = self.x_axis

            # reshape the data back and set it to its position
            self._mdict[name][0,0][7] = np.reshape(self.data,(self.data.shape[0] * self.data.shape[1], self.data.shape[2]), order='C')

            # set spectral map size (may change after cropping)
            self._mdict[name][0,0][5][0] = self.data.shape[:2]

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

        # TODO: experiment
        # new_masked_data = np.where(divisors == (2 * window_width + 1), 1, 0)

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