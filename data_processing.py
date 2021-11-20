import numpy as np
from numpy.lib.function_base import average
import scipy.io
import os

class Data:
    def __init__(self, file_name):
        # TODO: vyresit kde se to bude skladovat ta data
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        in_file = "./data/" + file_name
        mdict = {}
        matlab_data = scipy.io.loadmat(in_file, mdict=mdict)

        name = list(mdict)[-1] # last one is the name for of the data structure
        matlab_data = matlab_data[name][0,0]

        data = matlab_data[7]
        image_size = tuple(matlab_data[5][0]) # (Y size, X size) => num of rows, num of cols

        # data to work with
        self.x_axis = matlab_data[9][1][0][0]
        self.data = np.reshape(data,(image_size[0], image_size[1], data.shape[1]), order='F')
        self.maxes = np.max(self.data, axis=2) # good for looking at cosmic rays
        self.averages = np.mean(self.data, axis=2)
