
from __future__ import absolute_import, division, print_function, unicode_literals

import os.path

import pytest
import xarray as xr

from cfgrib import eccodes
from cfgrib import cfgrib_
from cfgrib import xarray_store

SAMPLE_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'sample-data')
TEST_DATA = os.path.join(SAMPLE_DATA_FOLDER, 'era5-levels-members.grib')
TEST_CORRUPTED = os.path.join(SAMPLE_DATA_FOLDER, 'era5-levels-corrupted.grib')


def test_CfGribDataStore():
    datastore = cfgrib_.CfGribDataStore(TEST_DATA, encode_cf=())
    expected = {'number': 10, 'dataDate': 2, 'dataTime': 2, 'level': 2, 'values': 7320}
    assert datastore.get_dimensions() == expected


def test_xarray_open_dataset():
    datastore = cfgrib_.CfGribDataStore(TEST_DATA, encode_cf=())
    res = xr.open_dataset(datastore)

    assert res.attrs['GRIB_edition'] == 1
    assert res['t'].attrs['GRIB_gridType'] == 'regular_ll'
    assert res['t'].attrs['GRIB_units'] == 'K'
    assert res['t'].dims == ('number', 'dataDate', 'dataTime', 'level', 'values')

    assert res['t'].mean() > 0.


def test_open_dataset():
    res = xarray_store.open_dataset(TEST_DATA)

    assert res.attrs['GRIB_edition'] == 1

    var = res['t']
    assert var.attrs['GRIB_gridType'] == 'regular_ll'
    assert var.attrs['units'] == 'K'
    assert var.dims == \
        ('number', 'time', 'isobaricInhPa', 'latitude', 'longitude')

    assert var.mean() > 0.

    with pytest.warns(FutureWarning):
        xarray_store.open_dataset(TEST_DATA, filter_by_keys={'typeOfLevel': 'isobaricInhPa'})


def test_open_dataset_corrupted():
    res = xarray_store.open_dataset(TEST_CORRUPTED)

    assert res.attrs['GRIB_edition'] == 1
    assert len(res.data_vars) == 1

    with pytest.raises(eccodes.EcCodesError):
        xarray_store.open_dataset(TEST_CORRUPTED, backend_kwargs={'grib_errors': 'strict'})


def test_open_dataset_encode_cf_time():
    backend_kwargs = {'encode_cf': ('time',)}
    res = xarray_store.open_dataset(TEST_DATA, backend_kwargs=backend_kwargs)

    assert res.attrs['GRIB_edition'] == 1
    assert res['t'].attrs['GRIB_gridType'] == 'regular_ll'
    assert res['t'].attrs['GRIB_units'] == 'K'
    assert res['t'].dims == ('number', 'time', 'level', 'values')

    assert res['t'].mean() > 0.


def test_open_dataset_encode_cf_vertical():
    backend_kwargs = {'encode_cf': ('vertical',)}
    res = xarray_store.open_dataset(TEST_DATA, backend_kwargs=backend_kwargs)

    var = res['t']
    assert var.dims == ('number', 'dataDate', 'dataTime', 'isobaricInhPa', 'values')

    assert var.mean() > 0.


def test_open_dataset_encode_cf_geography():
    backend_kwargs = {'encode_cf': ('geography',)}
    res = xarray_store.open_dataset(TEST_DATA, backend_kwargs=backend_kwargs)

    assert res.attrs['GRIB_edition'] == 1

    var = res['t']
    assert var.attrs['GRIB_gridType'] == 'regular_ll'
    assert var.attrs['GRIB_units'] == 'K'
    assert var.dims == ('number', 'dataDate', 'dataTime', 'level', 'latitude', 'longitude')

    assert var.mean() > 0.


def test_open_dataset_eccodes():
    res = xarray_store.open_dataset(TEST_DATA)

    assert res.attrs['GRIB_edition'] == 1

    var = res['t']
    assert var.attrs['GRIB_gridType'] == 'regular_ll'
    assert var.attrs['units'] == 'K'
    assert var.dims == ('number', 'time', 'isobaricInhPa', 'latitude', 'longitude')

    assert var.mean() > 0.
