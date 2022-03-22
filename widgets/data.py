import numpy as np
import scipy.io

# TODO: move somewhere else -> is not a widget
class Data:
    def __init__(self, in_file):
        self._mdict = {}
        self.x_axis = None
        self.data = None
        self.maxima = None
        self.averages = None
        self.Z_scores = None
        
        self.load_data(in_file)

    def load_data(self, in_file):
        # load only .mat data with expected structure
        try:
            # load from file
            matlab_data = scipy.io.loadmat(in_file, mdict=self._mdict)

            # extract relevant information
            name = list(self._mdict)[-1] # last one is the name of the data structure
            matlab_data = matlab_data[name][0,0]

            data = matlab_data[7]
            self.pure_data = data # TODO: data before reshaping -> only for current method testing
            image_size = tuple(matlab_data[5][0]) # num of rows, num of cols
            # units = matlab_data[9][1][1]
            # set attributes
            self.x_axis = matlab_data[9][1][0][0]
            self.data = np.reshape(data,(image_size[1], image_size[0], -1))
            self.maxima = np.max(self.data, axis=2) # good for looking at cosmic rays
            self.averages = np.mean(self.data, axis=2)
        except:
            print("Invalid file format or structure.")

    def save_data(self, out_file):
        # save as .mat file -> app looks for .mat extensions when looking for data files
        if not out_file.endswith(".mat"):
            out_file = out_file + ".mat"

        # m_dict is not empty
        if self._mdict:
            
            # keep the structure of input file (as in load_data)

            # name of the data structure
            name = list(self._mdict)[-1] 

            # set x axis values
            self._mdict[name][0,0][9][1][0][0] = self.x_axis

            # set data
            self._mdict[name][0,0][7] = np.reshape(self.data,(self.data.shape[0] * self.data.shape[1], self.data.shape[2]), order='C')

            # set spectral map size
            self._mdict[name][0,0][5][0] = self.data.shape[:2]

            scipy.io.savemat(out_file, mdict=self._mdict)

    def crop(self, spectra_start, spectra_end, ULC_x, ULC_y, LRC_x, LRC_y):
        x_axis_start = np.argmin(np.abs(self.x_axis - spectra_start))
        x_axis_end = np.argmin(np.abs(self.x_axis - spectra_end))
        self.x_axis = self.x_axis[x_axis_start:x_axis_end+1]
        self.data = self.data[ULC_x:LRC_x, ULC_y:LRC_y, x_axis_start:x_axis_end+1] # +1 -> upper bound is exclusive
        self.maxima = np.max(self.data, axis=2) # good for looking at cosmic rays
        self.averages = np.mean(self.data, axis=2)
    
    def _calculate_Z_scores(self):
        diff = np.diff(self.data, axis=2)
        M = np.median(diff, axis=2)
        wide_M = np.repeat(M[:,:,np.newaxis], diff.shape[2], 2)
        MAD = np.median(np.abs(diff-wide_M), axis=2)
        self.Z_scores = 0.6745 * (diff - wide_M) / np.repeat(MAD[:,:,np.newaxis], diff.shape[2], 2)
        self.Z_vlues = np.reshape(self.Z_scores, (np.prod(self.Z_scores.shape),)) # for histogram, maybe deleted TODO

    def get_spikes_positions(self, threshold):
        if self.Z_scores is None:
            self._calculate_Z_scores()
        spikes_positions = np.unique(np.vstack(np.where(np.abs(self.Z_scores) > threshold)[:2]).T, axis=0)
        return spikes_positions

