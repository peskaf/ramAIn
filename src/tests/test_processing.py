import pytest
from src.models.spectal_map import SpectralMap
import pathlib
import uuid
import numpy as np
import os
import copy

TEST_FILE_DIR = pathlib.Path(__file__).parent.resolve()
TEST_FILE_PATH = TEST_FILE_DIR.joinpath('test_data.mat')

def test_load_matlab():
    # TODO: check if we have data and download some testing sample otherwise
    sm = SpectralMap(TEST_FILE_PATH)
    data, x_axis = sm.data, sm.x_axis

    assert data.shape == (30, 40, 1600)
    assert x_axis.shape == (1600,)

def test_save_matlab():
    test_file2_name = f'test_data_{uuid.uuid4()}.mat'
    test_file2_path = TEST_FILE_DIR.joinpath(test_file2_name)
    sm = SpectralMap(TEST_FILE_PATH)
    sm.save_matlab(TEST_FILE_DIR, test_file2_name)
    sm2 = SpectralMap(test_file2_path)
    try:
        assert np.array_equal(sm.data, sm2.data)
    finally:
        os.remove(test_file2_path)
    
def test_map_cropping():
    sm = SpectralMap(TEST_FILE_PATH)

    left, top, right, bottom = 5, 3, 20, 30

    sm2 = copy.deepcopy(sm)
    sm2.crop_spectral_map(left, top, right, bottom)

    assert sm2.shape == (bottom - top, right - left, sm.shape[2])
    assert np.array_equal(sm.data[top:bottom, left:right], sm2.data)

def test_spectra_cropping_relative():
    sm = SpectralMap(TEST_FILE_PATH)

    left, right = 15, 20

    sm2 = copy.deepcopy(sm)
    sm2.crop_spectra_relative(left, right)

    assert sm2.shape == (*sm.shape[:2], sm.shape[2] - (left + right))

def test_spectra_cropping_absolute():
    sm = SpectralMap(TEST_FILE_PATH)

    left_val, right_val = 417.6, 2987.0
    points_num = ((sm.x_axis >= left_val) & (sm.x_axis <= right_val)).sum()

    sm2 = copy.deepcopy(sm)
    sm2.crop_spectra_absolute(left_val, right_val)

    assert sm2.x_axis.shape == (points_num,)
    assert sm2.shape == (*sm.shape[:2], points_num)

def test_manual_removal():
    sm = SpectralMap(TEST_FILE_PATH)
    sm2 = copy.deepcopy(sm)
    
    start, end = 518.6, 627.1
    spectrum_x_index, spectrum_y_index = 2, 14

    sm2.interpolate_withing_range(spectrum_x_index, spectrum_y_index, start, end)

    sm_spectrum = sm.data[spectrum_x_index, spectrum_y_index]
    sm2_spectrum = sm2.data[spectrum_x_index, spectrum_y_index]

    assert sm2_spectrum.shape == sm_spectrum.shape
    assert sm2_spectrum[np.argmax((sm.x_axis >= start))] == sm_spectrum[np.argmax((sm.x_axis >= start))]

def test_auto_removal():
    sm = SpectralMap(TEST_FILE_PATH)
    sm2 = copy.deepcopy(sm)

    sm.auto_spike_removal()

    # test data has no artificial spike
    assert np.array_equal(sm.data, sm2.data)

    # create our own spike
    sm.data[0, 0, 50] = 1000

    sm.auto_spike_removal()
    
    # that one should be removed
    assert not np.array_equal(sm.data[0, 0], sm2.data[0, 0])

    # other parts of the maps should not be affected
    assert np.array_equal(sm.data[1:, 1:], sm2.data[1:, 1:])
