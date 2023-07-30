import scipy.io
import numpy as np
from typing import Union, Optional
from pathlib import Path

import sys
sys.path.append('.')
sys.path.append('..')

from src.utils import paths
from sys import getsizeof


class SpectralMap():

    def __init__(self, in_file_path: Union[str, Path]) -> None:

        self.in_file = in_file_path

        self._mdict = {} # dict to save matlab dict into
        self.x_axis = None
        self.data = None

        # keep?
        self.maxima = None
        self.averages = None
        self.Z_scores = None
        self.components = []
        self.spikes = {}

        # Now load from matlab, then identify format and load according to it
        self.load_matlab()

    @property
    def shape(self):
        return self.data.shape

    def load_matlab(self) -> None:
        """
        Compatible with spectroscopes: TODO
        - ...
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
            map_shape = tuple(matlab_data[5][0])

            self.units = matlab_data[9][1][1]

            self.x_axis = matlab_data[9][1][0][0]

            self.data = np.reshape(data,(map_shape[1], map_shape[0], -1))

            #print(self.data.nbytes / 1024 / 1024)
            
            # ??
            self.maxima = np.max(self.data, axis=2)
            self.averages = np.mean(self.data, axis=2)
    
            # TODO: assert or if with possible raise?
            assert self.x_axis.shape[0] == self.data.shape[-1], "x-axis shape does not match with the data"

        except Exception as e:
            raise Exception(f"{self.in_file}: file could not be loaded; {e}")
            # TODO: what should be returned so that the app still works?
            # -> some window stating this message if not auto processing, else skip and log this message
    
    def save_matlab(self, out_folder_path: Union[str, Path], file_name: Optional[Union[str, Path]]=None, file_tag: Optional[str]=None) -> None:

        out_file = paths.create_new_file_name(out_folder_path, file_name if file_name else self.in_file, file_tag)
        
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

if __name__=='__main__':
    sm = SpectralMap('/home/filip/ramAIn/data/Glenodinium.mat')