# -*- coding: utf-8 -*-
import numpy as np

__all__ = ['big_number_verify']


def big_number_verify(x, mean, stddev, n_samples, scale=4.):
    np.testing.assert_array_less(
        np.abs(x - mean), stddev * scale / np.sqrt(n_samples),
        err_msg='away from expected mean by %s stddev' % scale
    )
