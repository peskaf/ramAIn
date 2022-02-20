import numpy as np
import scipy.io
# TODO: move somewhere else -> is not a widget
class Data:
    def __init__(self, in_file):

        # ODSUD DÁL -> PŘEDPOKLAD, ŽE JSEM OPRAVDU DOSTAL MATLABOVSKÝ SOUBOR!!! -> ZAJISTIT VE VOLAJÍCÍM, ABYCH HO NEDOSTAL
        mdict = {}
        matlab_data = scipy.io.loadmat(in_file, mdict=mdict)

        name = list(mdict)[-1] # last one is the name for of the data structure
        matlab_data = matlab_data[name][0,0]

        data = matlab_data[7]
        image_size = tuple(matlab_data[5][0]) # (Y size, X size) => num of rows, num of cols
        units = matlab_data[9][1][1]

        self.x_axis = matlab_data[9][1][0][0]
        self.data = np.reshape(data,(image_size[0], image_size[1], data.shape[1]), order='F')
        self.maxima = np.max(self.data, axis=2) # good for looking at cosmic rays
        self.minima = np.min(self.data, axis=2)
        self.averages = np.mean(self.data, axis=2)

    # TODO: crop, load, save, ... 
