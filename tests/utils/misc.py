# -*- coding: utf-8 -*-
import os
import unittest

import numpy as np
import six

__all__ = ['big_number_verify', 'model_test']


def big_number_verify(x, mean, stddev, n_samples, scale=4.):
    np.testing.assert_array_less(
        np.abs(x - mean), stddev * scale / np.sqrt(n_samples),
        err_msg='away from expected mean by %s stddev' % scale
    )


def model_testing_enabled():
    flag = os.environ.get('MLCOMP_TEST_MODELS', '').lower()
    return flag in ('1', 'on', 'yes', 'true')


def model_test(method):
    @six.wraps(method)
    def inner(*args, **kwargs):
        method = unittest.skipUnless(
            model_testing_enabled(), 'Model testing is not enabled.')
        return method(*args, **kwargs)
    return inner
