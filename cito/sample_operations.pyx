
import numpy as np
cimport numpy as np

from scipy.stats import norm

import pyximport

np.import_array()

pyximport.install()


def shrink(np.ndarray[np.uint16_t] values, Py_ssize_t n):
    cdef np.ndarray[np.uint16_t, ndim=1] shrunk_values = np.zeros(values.size / n,
                                                                 dtype=np.uint16)
    cdef Py_ssize_t i
    print(values.size)
    for i in range(values.size):
        shrunk_values[i/n] += values[i]
    return shrunk_values


def filter_samples(np.ndarray[np.uint16_t] values):
    """Apply a filter

    :rtype : dict
    :param values: Values to filter
    :type values: np.array
    """
    cdef Py_ssize_t i, j
    cdef Py_ssize_t filter_range = 100
    cdef np.float_t temp_val = 0.0


    cdef np.ndarray[np.float_t, ndim=1] filter_values = np.zeros(6*filter_range, dtype=np.float)
    cdef np.ndarray[np.uint16_t, ndim=1] old_values = values.copy()
    cdef np.ndarray[np.uint16_t, ndim=1] new_values = np.zeros_like(values, dtype=np.uint16)
    #new_values = np.zeros_like(values)

    print('\tprefilter')
    my_filter = norm(0, filter_range) # mu=0, sigma=100
    for j in range(-3*filter_range, 3*filter_range):
        filter_values[j] = my_filter.pdf(j)

    print('\tapply_filter')
    for i in range(old_values.size):
        for j in range(-3 * filter_range, 3*filter_range):
            if i + j > 0 and i + j < old_values.size:
                temp_val = old_values[i] * filter_values[j]
                new_values[i + j] += <np.uint16_t>(temp_val)
                #print(i, j, old_values[i], temp_val, new_values[i+j])

    return new_values

