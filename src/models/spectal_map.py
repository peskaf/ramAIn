import scipy.io
import numpy as np
from typing import Union, Optional
from pathlib import Path

import sys
sys.path.append('.')
sys.path.append('..')

from src.utils import paths
from src.spectra_processing.cropping import cropping
from src.spectra_processing.artifacts_removal import manual_removal, custom_auto_removal
from src.spectra_processing.background_removal import math_morpho, imodpoly, poly
from src.spectra_processing.linearization import linearization

class SpectralMap():

    def __init__(self, in_file_path: Union[str, Path]) -> None:

        self.in_file = in_file_path

        self._mdict = {} # dict to save matlab dict into
        self.x_axis = None
        self._data = None
        self._spike_info = {}

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

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value

        self.maxima = np.max(self.data, axis=2)
        self.averages = np.mean(self.data, axis=2)
        self._spike_info = {}

    def load_matlab(self) -> None:
        """
        Compatible with spectroscopes: TODO
        - ...
        """

        try:
            # load .mat data with expected structure
            matlab_data = scipy.io.loadmat(self.in_file, mdict=self._mdict)


            name = list(self._mdict)[-1]
            matlab_data = matlab_data[name][0,0]

            data = matlab_data[7]

            map_shape = tuple(matlab_data[5][0])

            self.units = matlab_data[9][1][1]
            self.x_axis = matlab_data[9][1][0][0]
            self.data = np.reshape(data,(map_shape[1], map_shape[0], -1))

            #print(self.data.nbytes / 1024 / 1024)
    
            # TODO: assert or if with possible raise?
            assert self.x_axis.shape[0] == self.data.shape[-1], "x-axis shape does not match with the data"

        except Exception as e:
            raise Exception(f"{self.in_file}: file could not be loaded; {e}")
            # TODO: what should be returned so that the app still works?
            # -> some window stating this message if not auto processing, else skip and log this message
    
    def save_matlab(self, out_folder_path: Union[str, Path], file_name: Optional[Union[str, Path]]=None, file_tag: Optional[str]=None) -> None:

        out_file = paths.create_new_file_name(out_folder_path, file_name if file_name else self.in_file, file_tag)
        
        try:
            name = list(self._mdict)[-1] 
            self._mdict[name][0,0][9][1][0] = [self.x_axis]
            self._mdict[name][0,0][7] = np.reshape(self.data,(self.data.shape[0] * self.data.shape[1], -1), order='C')
            self._mdict[name][0,0][5][0] = self.data.shape[:2][::-1]

            scipy.io.savemat(out_file, appendmat=True, mdict=self._mdict)

        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")
        
    def crop_spectra_absolute(self, crop_start: float, crop_end: float) -> None:
        self.data, self.x_axis = cropping.crop_spectra_absolute(self.data, self.x_axis, crop_start, crop_end)

    def crop_spectra_relative(self, crop_first: int, crop_last: int) -> None:
        self.data, self.x_axis = cropping.crop_spectra_relative(self.data, self.x_axis, crop_first, crop_last)

    def crop_spectral_map(self, left: int, top: int, right: int, bottom: int) -> None:
        self.data = cropping.crop_map(self.data, left, top, right, bottom)
    
    def interpolate_withing_range(self, x_index: int, y_index: int, start: float, end: float) -> None:
        self.data[x_index, y_index] = manual_removal.interpolate_within_range(self.data[x_index, y_index], self.x_axis, start, end)
    
    def _calculate_spikes_indices(self) -> None:
        map_indices, peak_positions = custom_auto_removal.calculate_spikes_indices(self.data, self.x_axis)

        self._spike_info['map_indices'] = map_indices
        self._spike_info['peak_positions'] = peak_positions

    def auto_spike_removal(self) -> None:
        if not self._spike_info:
            self._calculate_spikes_indices()
        self.data = custom_auto_removal.remove_spikes(self.data, self._spike_info['map_indices'], self._spike_info['peak_positions'])

    # TODO: signals?
    def background_removal_math_morpho(self, ignore_water: bool) -> None:
        self.data = math_morpho.math_morpho(self.data, self.x_axis, ignore_water)

    def background_removal_imodpoly(self, degree: int, ignore_water: bool) -> None:
        self.data = imodpoly.imodpoly(self.data, self.x_axis, degree, ignore_water)

    def background_removal_poly(self, degree: int, ignore_water: bool) -> None:
        self.data = poly.poly(self.data, self.x_axis, degree, ignore_water)

    def linearization(self, step: float) -> None:
        self.data, self.x_axis = linearization.linearize(self.data, self.x_axis, step)

    

if __name__=='__main__':
    data_path = '/home/filip/ramAIn/data/Gefionella.mat'
    data_path_test = '/home/filip/ramAIn/src/tests/test_data.mat'
    sm = SpectralMap(data_path)
    import matplotlib.pyplot as plt
    print(sm.data[0].shape)
    print(sm.x_axis)
    plt.imshow(sm.averages)
    plt.show()