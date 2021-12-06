import numpy as np
from numpy.lib.function_base import average
import scipy.io

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

        # data to work with # TODO: vyresit jednotky
        if units == "nm":
            self.x_axis = [10**7 / x for x in matlab_data[9][1][0][0]] # nefunguje! je potřeba Excitation Wavelength a pak podle https://en.wikipedia.org/wiki/Raman_spectroscopy#Raman_shift
        else:
            self.x_axis = matlab_data[9][1][0][0]
        self.data = np.reshape(data,(image_size[0], image_size[1], data.shape[1]), order='F')
        self.maxima = np.max(self.data, axis=2) # good for looking at cosmic rays
        self.minima = np.min(self.data, axis=2)
        self.averages = np.mean(self.data, axis=2)
