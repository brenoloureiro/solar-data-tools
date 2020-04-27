# -*- coding: utf-8 -*-
''' Solar Noon Module

This module contains functions for estimating solar noon on each day in a
PV power or irradiance data set. All functions assume that the data has been
cleaned and put into a 2-D array or power matrix form
(see: `solardatatools.data_transforms`)

For low-frequency data set (e.g. 15-minute), the energy center of mass approach
tends to give a better estimate of solar noon than the sunrise/sunset approach.

'''
import numpy as np
from solardatatools.daytime import find_daytime

def energy_com(data):
    """ Calculate the energy center of mass for each day, and use this quantity
    as an estimate for solar noon.

    Function infers time stamps from the length of the first axis of the 2-D
    data array.

    :param data: PV power matrix as generated by `make_2d` from `solardatatools.data_transforms`
    :return: A 1-D array, containing the solar noon estimate for each day in the data set
    """
    num_meas_per_hour = data.shape[0] / 24
    x = np.arange(0, 24, 1. / num_meas_per_hour)
    div1 = np.dot(x, data)
    div2 = np.sum(data, axis=0)
    com = np.empty_like(div1)
    com[:] = np.nan
    msk = div2 != 0
    com[msk] = np.divide(div1[msk], div2[msk])
    return com

def avg_sunrise_sunset(data_in, threshold=0.01):
    """ Calculate the sunrise time and sunset time for each day, and use the
    average of these two values as an estimate for solar noon.

    :param data_in: PV power matrix as generated by `make_2d` from `solardatatools.data_transforms`
    :return: A 1-D array, containing the solar noon estimate for each day in the data set
    """
    data = np.copy(data_in).astype(np.float)
    num_meas_per_hour = data.shape[0] / 24
    x = np.arange(0, 24, 1. / num_meas_per_hour)
    night_msk = ~find_daytime(data_in, threshold=threshold)
    data[night_msk] = np.nan
    good_vals = (~np.isnan(data)).astype(int)
    sunrise_idxs = np.argmax(good_vals, axis=0)
    sunset_idxs = data.shape[0] - np.argmax(np.flip(good_vals, 0), axis=0)
    sunset_idxs[sunset_idxs == data.shape[0]] = data.shape[0] - 1
    hour_of_day = x
    sunrise_times = hour_of_day[sunrise_idxs]
    sunset_times = hour_of_day[sunset_idxs]
    solar_noon = (sunrise_times + sunset_times) / 2
    return solar_noon
