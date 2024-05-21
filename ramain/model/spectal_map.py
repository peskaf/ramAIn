import scipy.io
import numpy as np
from typing import Union, Optional
from pathlib import Path

import sys

sys.path.append(".")
sys.path.append("..")

from ramain.utils import paths
from ramain.spectra_processing.cropping import cropping
from ramain.spectra_processing.artifacts_removal import (
    manual_removal,
    custom_auto_removal,
)
from ramain.spectra_processing.background_removal import (
    math_morpho,
    imodpoly,
    poly,
    airpls,
    bubblefill,
)
from ramain.spectra_processing.linearization import linearization
from ramain.spectra_processing.decomposition import PCA, NMF
from ramain.spectra_processing.export import to_graphics, to_text
from ramain.spectra_processing.smoothing import whittaker, savgol
from ramain.spectra_processing.normalization import water_normalization

from ramain.utils.settings import SETTINGS

from PySide6.QtCore import Signal


class SpectralMap:
    def __init__(self, in_file_path: Union[str, Path]) -> None:
        self.in_file = in_file_path

        self._mdict = {}  # dict to save matlab dict into
        self.x_axis = None
        self._data = None
        self._spike_info = {}
        self._water_info = {}
        self._components = []
        self.maxima = None
        self.averages = None

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
        self._water_info = {}
        self._components = []

    def load_matlab(self) -> None:
        """
        Compatible with spectroscopes: TODO
        - ...
        """

        try:
            # load .mat data with expected structure
            matlab_data = scipy.io.loadmat(self.in_file, mdict=self._mdict)

            name = list(self._mdict)[-1]
            matlab_data = matlab_data[name][0, 0]

            data = matlab_data[7]

            map_shape = tuple(matlab_data[5][0])

            self.units = matlab_data[9][1][1]
            self.x_axis = matlab_data[9][1][0][0]
            self.data = np.reshape(data, (map_shape[1], map_shape[0], -1))

            # print(self.data.nbytes / 1024 / 1024)

            # TODO: assert or if with possible raise?
            assert (
                self.x_axis.shape[0] == self.data.shape[-1]
            ), "x-axis shape does not match with the data"

        except Exception as e:
            print(e)
            raise Exception(f"{self.in_file}: file could not be loaded; {e}")
            # TODO: what should be returned so that the app still works?
            # -> some window stating this message if not auto processing, else skip and log this message

    def save_matlab(
        self,
        out_folder_path: Union[str, Path],
        file_tag: Optional[str] = None,
        file_name: Optional[Union[str, Path]] = None,
    ) -> None:
        FALLBACK_EXTENSION = ".mat"
        out_file = paths.create_new_file_name(
            out_folder_path,
            file_name if file_name else self.in_file,
            FALLBACK_EXTENSION,
            file_tag,
        )

        try:
            name = list(self._mdict)[-1]
            self._mdict[name][0, 0][9][1][0] = [self.x_axis]
            self._mdict[name][0, 0][7] = np.reshape(
                self.data, (self.data.shape[0] * self.data.shape[1], -1), order="C"
            )
            self._mdict[name][0, 0][5][0] = self.data.shape[:2][::-1]

            scipy.io.savemat(out_file, appendmat=True, mdict=self._mdict)

        except Exception as e:
            raise Exception(f"{self.in_file}: {e}")

    def crop_spectra_absolute(self, crop_start: float, crop_end: float) -> None:
        self.data, self.x_axis = cropping.crop_spectra_absolute(
            self.data, self.x_axis, crop_start, crop_end
        )

    def crop_spectra_relative(self, crop_first: int, crop_last: int) -> None:
        self.data, self.x_axis = cropping.crop_spectra_relative(
            self.data, self.x_axis, crop_first, crop_last
        )

    def crop_spectral_map(self, left: int, top: int, right: int, bottom: int) -> None:
        self.data = cropping.crop_map(self.data, left, top, right, bottom)

    def interpolate_withing_range(
        self, x_index: int, y_index: int, start: float, end: float
    ) -> None:
        self.data[x_index, y_index] = manual_removal.interpolate_within_range(
            self.data[x_index, y_index], self.x_axis, start, end
        )

    def _calculate_spikes_indices(self) -> None:
        map_indices, peak_positions = custom_auto_removal.calculate_spikes_indices(
            self.data, self.x_axis
        )

        self._spike_info["map_indices"] = map_indices
        self._spike_info["peak_positions"] = peak_positions

    def auto_spike_removal(self) -> None:
        if not self._spike_info:
            self._calculate_spikes_indices()
        self.data = custom_auto_removal.remove_spikes(
            self.data,
            self._spike_info["map_indices"],
            self._spike_info["peak_positions"],
        )

    def background_removal_math_morpho(
        self,
        ignore_water: bool,
        signal_to_emit: Signal = None,
        one_spectrum: Optional[np.ndarray] = None,
    ) -> Optional[np.ndarray]:
        if one_spectrum is not None:
            return math_morpho._math_morpho_on_spectrum(
                one_spectrum, self.x_axis, ignore_water
            )
        self.data = math_morpho.math_morpho(
            self.data, self.x_axis, ignore_water, signal_to_emit
        )

    def background_removal_imodpoly(
        self,
        degree: int,
        ignore_water: bool,
        signal_to_emit: Signal = None,
        one_spectrum: Optional[np.ndarray] = None,
    ) -> Optional[np.ndarray]:
        if one_spectrum is not None:
            return imodpoly.imodpoly_bg(one_spectrum, self.x_axis, degree, ignore_water)
        self.data = imodpoly.imodpoly(
            self.data, self.x_axis, degree, ignore_water, signal_to_emit
        )

    def background_removal_poly(
        self, degree: int, ignore_water: bool, one_spectrum: Optional[np.ndarray] = None
    ) -> Optional[np.ndarray]:
        if one_spectrum is not None:
            return poly.poly_bg(one_spectrum, self.x_axis, degree, ignore_water)
        self.data = poly.poly(self.data, self.x_axis, degree, ignore_water)

    def background_removal_airpls(
        self,
        lambda_: int,
        one_spectrum: Optional[np.ndarray] = None,
    ) -> Optional[np.ndarray]:
        if one_spectrum is not None:
            return airpls.airPLS_spectrum(one_spectrum, self.x_axis, lambda_)
        self.data = airpls.airPLS(self.data, lambda_)

    def background_removal_bubblefill(
        self,
        bubble_size: int,
        water_bubble_size: int,
        signal_to_emit: Signal = None,
        one_spectrum: Optional[np.ndarray] = None,
    ) -> None:
        # TODO: tune this
        min_bubble_widths = [
            (bubble_size if (n < 3100 or n > 3750) else water_bubble_size)
            for n in self.x_axis
        ]
        if one_spectrum is not None:
            return bubblefill.bubblefill_bg(
                one_spectrum, self.x_axis, min_bubble_widths
            )
        self.data = bubblefill.bubblefill(
            self.data, self.x_axis, min_bubble_widths, signal_to_emit=signal_to_emit
        )

    def linearization(self, step: float) -> None:
        self.data, self.x_axis = linearization.linearize(self.data, self.x_axis, step)

    def decomposition_PCA(
        self,
        n_components: int,
    ) -> None:
        self._components = PCA.PCA(self.data, n_components)

    def decomposition_NMF(
        self,
        n_components: int,
        signal_to_emit: Signal = None,
    ) -> None:
        self._components = NMF.NMF(self.data, n_components, signal_to_emit)

    def export_to_graphics(
        self,
        file_format: str,
        out_dir: str = "",
        file_tag: str = "",
        file_name: str = "",
    ) -> None:
        cmap = str(SETTINGS.value("spectral_map/cmap"))
        to_graphics.export_components_graphics(
            self.data,
            self.x_axis,
            self._components,
            file_format,
            self.in_file,
            cmap,
            out_dir,
            file_name,
            file_tag,
        )

    def export_to_text(
        self, out_dir: str = "", file_tag: str = "", file_name: str = ""
    ) -> None:
        to_text.export_components_txt(
            self._components, self.x_axis, self.in_file, out_dir, file_name, file_tag
        )

    def smoothing_whittaker(
        self, lam: int = 1600, diff: int = 2, one_spectrum: Optional[np.ndarray] = None
    ):
        if one_spectrum is not None:
            return whittaker.whittaker(one_spectrum, lam, diff)
        self.data = whittaker.whittaker(self.data, lam, diff)

    def smoothing_savgol(
        self,
        window_length: int = 5,
        polyorder: int = 2,
        one_spectrum: Optional[np.ndarray] = None,
    ):
        if one_spectrum is not None:
            return savgol.savgol(one_spectrum, window_length, polyorder)
        self.data = savgol.savgol(self.data, window_length, polyorder)

    def _calculate_average_water(self, threshold: float = 0.3) -> None:
        average_water, water_mask = water_normalization._get_average_water(
            self.data, self.x_axis
        )

        self._water_info["average_water"] = average_water
        indices = np.where(water_mask == 1)
        self._water_info["water_indices"] = np.array(list(zip(indices[0], indices[1])))

    def water_normalization(self) -> None:
        if not self._water_info:
            self._calculate_average_water()

        self.data = water_normalization.water_normalization(
            self.data, self.x_axis, self._water_info["average_water"]
        )


if __name__ == "__main__":
    data_path = "/home/filip/ramAIn/data/Gefionella.mat"
    data_path_test = "/home/filip/ramAIn/src/tests/test_data.mat"
    sm = SpectralMap(data_path)
    import matplotlib.pyplot as plt

    print(sm.data[0].shape)
    print(sm.x_axis)
    plt.imshow(sm.averages)
    plt.show()
