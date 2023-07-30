import pytest
from src.models.spectal_map import SpectralMap
from src.spectra_processing.cropping import cropping
import pathlib
import uuid
import numpy as np
import os

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
    og_shape = sm.shape
    left, top, right, bottom = 5, 3, 20, 30 
    sm = cropping.crop_map(sm, left, top, right, bottom)
    assert sm.shape == (og_shape[0] - ())