
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pytest
import xarray as xr

from cf2cdm import cfcoords


@pytest.fixture
def da1():
    latitude = [0., 0.5]
    longitude = [10., 10.5]
    time = ['2017-12-01T00:00:00', '2017-12-01T12:00:00', '2017-12-02T00:00:00']
    level = [950, 500]
    data = xr.DataArray(
        np.zeros((2, 2, 3, 2), dtype='float32'),
        coords=[
            ('lat', latitude, {'units': 'degrees_north'}),
            ('lon', longitude, {'units': 'degrees_east'}),
            ('ref_time', np.array(time, dtype=np.datetime64),
                {'standard_name': 'forecast_reference_time'}),
            ('level', np.array(level), {'units': 'hPa'}),
        ])
    return data


@pytest.fixture
def da2():
    latitude = [0., 0.5]
    longitude = [10., 10.5]
    time = ['2017-12-01T00:00:00', '2017-12-01T12:00:00', '2017-12-02T00:00:00']
    level = [950, 500]
    data = xr.DataArray(
        np.zeros((2, 2, 3, 2), dtype='float32'),
        coords=[
            ('lat', latitude, {'units': 'degrees_north'}),
            ('lon', longitude, {'units': 'degrees_east'}),
            ('time', np.array(time, dtype=np.datetime64)),
            ('level', np.array(level), {'units': 'hPa'}),
        ])
    return data


@pytest.fixture
def da3():
    latitude = [0., 0.5]
    longitude = [10., 10.5]
    step = [0, 24, 48]
    time = ['2017-12-01T00:00:00', '2017-12-01T12:00:00']
    level = [950, 500]
    data = xr.DataArray(
        np.zeros((2, 2, 3, 2, 2), dtype='float32'),
        coords=[
            ('lat', latitude, {'units': 'degrees_north'}),
            ('lon', longitude, {'units': 'degrees_east'}),
            ('step', np.array(step, dtype=np.timedelta64), {'standard_name': 'forecast_period'}),
            ('ref_time', np.array(time, dtype=np.datetime64),
                {'standard_name': 'forecast_reference_time'}),
            ('level', np.array(level), {'units': 'hPa'}),
        ])

    return data


def test_match_values():
    mapping = {'callable': len, 'int': 1}
    res = cfcoords.match_values(callable, mapping)

    assert res == ['callable']


def test_coord_translator(da1):
    res = cfcoords.coord_translator('level', 'hPa', lambda x: False, 'level', da1)
    assert da1.equals(res)

    with pytest.raises(ValueError):
        cfcoords.coord_translator('level', 'hPa', lambda x: True, 'level', da1)

    res = cfcoords.coord_translator('level', 'hPa', cfcoords.is_vertical_pressure, 'level', da1)
    assert da1.equals(res)

    with pytest.raises(ValueError):
        cfcoords.coord_translator('level', 'hPa', cfcoords.is_latitude, 'level', da1)

    res = cfcoords.coord_translator('level', 'Pa', cfcoords.is_vertical_pressure, 'level', da1)
    assert not da1.equals(res)

    res = cfcoords.coord_translator('step', 'h', cfcoords.is_forecast_period, 'step', da1)
    assert da1.equals(res)


def test_translate_coords(da1, da2):
    result = cfcoords.translate_coords(da1)

    assert 'latitude' in result.coords
    assert 'longitude' in result.coords
    assert 'time' in result.coords

    result = cfcoords.translate_coords(da2)

    assert 'latitude' in result.coords
    assert 'longitude' in result.coords
    assert 'valid_time' in result.coords


def test_ensure_valid_time(da1, da3):
    res1 = cfcoords.ensure_valid_time(da1.squeeze())
    res2 = cfcoords.ensure_valid_time(res1)

    assert 'valid_time' in res1.coords
    assert res2 is res1

    res1 = cfcoords.ensure_valid_time(da3.isel(ref_time=0).squeeze())
    res2 = cfcoords.ensure_valid_time(res1)

    assert 'valid_time' in res1.coords
    assert res2 is res1

    res1 = cfcoords.ensure_valid_time(da3.squeeze())
    assert 'valid_time' in res1.coords
    coords1 = res1.coords
    assert coords1['valid_time'].shape == (coords1['ref_time'].size, coords1['step'].size)

    with pytest.raises(ValueError):
        cfcoords.ensure_valid_time(da3.mean(dim='ref_time').squeeze())
