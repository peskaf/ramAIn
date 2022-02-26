import numpy as np
import scipy.io

# OK
# TODO: move somewhere else -> is not a widget
class Data:
    def __init__(self, in_file):
        # attributes
        self._mdict = {}
        self.x_axis = None
        self.data = None
        self.maxima = None
        self.minima = None
        self.averages = None
        
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
            self.pure_data = data # TODO: delete :))
            image_size = tuple(matlab_data[5][0]) # (Y size, X size) => num of rows, num of cols
            # units = matlab_data[9][1][1]

            # set attributes
            self.x_axis = matlab_data[9][1][0][0]
            self.data = np.reshape(data,(image_size[0], image_size[1], data.shape[1]), order='F')

            self.maxima = np.max(self.data, axis=2) # good for looking at cosmic rays
            self.minima = np.min(self.data, axis=2)
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
            self._mdict[name][0,0][7] = np.reshape(self.data,(self.data.shape[0] * self.data.shape[1], self.data.shape[2]), order='F')

            # set spectral map size
            self._mdict[name][0,0][5][0] = self.data.shape[:2]

            scipy.io.savemat(out_file, mdict=self._mdict)
