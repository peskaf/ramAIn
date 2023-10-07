import pytest
from src.models.spectal_map import SpectralMap
import pathlib
import uuid
import numpy as np
import os
import copy
from sklearn.utils._testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning


TEST_FILE_DIR = pathlib.Path(__file__).parent.resolve()
TEST_FILE_PATH = TEST_FILE_DIR.joinpath("test_data.mat")


def test_load_matlab():
    # TODO: check if we have data and download some testing sample otherwise
    sm = SpectralMap(TEST_FILE_PATH)
    data, x_axis = sm.data, sm.x_axis

    assert data.shape == (30, 40, 1600)
    assert x_axis.shape == (1600,)


def test_save_matlab():
    test_file2_name = f"test_data_{uuid.uuid4()}.mat"
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
    assert (
        sm2_spectrum[np.argmax((sm.x_axis >= start))]
        == sm_spectrum[np.argmax((sm.x_axis >= start))]
    )


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


def test_math_morpho():
    sm = SpectralMap(TEST_FILE_PATH)
    sm2 = copy.deepcopy(sm)

    sm.background_removal_math_morpho(True)

    assert not np.array_equal(sm.data, sm2.data)


def test_airpls():
    sm = SpectralMap(TEST_FILE_PATH)
    sm2 = copy.deepcopy(sm)

    sm.background_removal_airpls(10**4)

    assert not np.array_equal(sm.data, sm2.data)


def test_imodpoly():
    sm = SpectralMap(TEST_FILE_PATH)
    sm2 = copy.deepcopy(sm)

    sm.background_removal_imodpoly(2, True)

    assert not np.array_equal(sm.data, sm2.data)


def test_poly():
    sm = SpectralMap(TEST_FILE_PATH)
    sm2 = copy.deepcopy(sm)

    sm.background_removal_poly(2, True)

    assert not np.array_equal(sm.data, sm2.data)


def test_linearize():
    sm = SpectralMap(TEST_FILE_PATH)

    steps = [0.2, 0.5, 1.0, 1.6]
    for step in steps:
        sm.linearization(step)
        x_axis = sm.x_axis
        diffs = np.diff(x_axis, 1)
        step_array = np.full_like(diffs, step)
        assert np.allclose(diffs, step_array, rtol=1e-9, atol=1e-9)


def test_PCA():
    sm = SpectralMap(TEST_FILE_PATH)
    assert len(sm._components) is 0
    components_cnt = [1, 2, 3, 4, 5, 6]
    for comp_cnt in components_cnt:
        sm.decomposition_PCA(n_components=comp_cnt)
        assert type(sm._components) is list
        assert len(sm._components) == comp_cnt
        assert type(sm._components[0]) is dict


@ignore_warnings(category=ConvergenceWarning)
def test_NMF():
    sm = SpectralMap(TEST_FILE_PATH)
    assert len(sm._components) is 0
    components_cnt = [1, 3, 6]
    for comp_cnt in components_cnt:
        sm.decomposition_NMF(n_components=comp_cnt)
        assert type(sm._components) is list
        assert len(sm._components) == comp_cnt
        assert type(sm._components[0]) is dict


def test_export_text():
    sm = SpectralMap(TEST_FILE_PATH)
    n_comps = 3
    sm.decomposition_PCA(n_comps)

    try:
        out_file = f"export_{uuid.uuid4()}.txt"
        out_file_path = TEST_FILE_DIR.joinpath(out_file)
        sm.export_to_text(file_name=out_file_path)
        assert os.path.exists(out_file_path)
        data_array = np.loadtxt(out_file_path, dtype=np.float32, delimiter="\t")
        assert data_array.shape == (sm.x_axis.shape[0], n_comps + 1)
    finally:
        os.remove(out_file_path)

    try:
        tag = "bb"
        sm.export_to_text(out_dir=TEST_FILE_DIR, file_tag=tag)
        in_file_name, _ = os.path.basename(sm.in_file).split(".")
        out_file_path = os.path.join(TEST_FILE_DIR, in_file_name + tag + "." + "txt")
        assert os.path.exists(out_file_path)
        data_array = np.loadtxt(out_file_path, dtype=np.float32, delimiter="\t")
        assert data_array.shape == (sm.x_axis.shape[0], n_comps + 1)
    finally:
        os.remove(out_file_path)


def test_export_graphics():
    sm = SpectralMap(TEST_FILE_PATH)
    n_comps = 3
    sm.decomposition_PCA(n_comps)

    try:
        out_file = f"export_{uuid.uuid4()}.png"
        out_file_path = TEST_FILE_DIR.joinpath(out_file)
        sm.export_to_graphics(file_format="png", file_name=out_file_path)
        assert os.path.exists(out_file_path)
    finally:
        os.remove(out_file_path)

    try:
        tag = "bb"
        sm.export_to_graphics(file_format="png", out_dir=TEST_FILE_DIR, file_tag=tag)
        in_file_name, _ = os.path.basename(sm.in_file).split(".")
        out_file_path = os.path.join(TEST_FILE_DIR, in_file_name + tag + "." + "png")
        assert os.path.exists(out_file_path)
    finally:
        os.remove(out_file_path)
