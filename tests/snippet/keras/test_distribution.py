# -*- coding: utf-8 -*-
import unittest

import six
import numpy as np
from keras import backend as K
from keras.engine import Input
from logging import getLogger

from mlcomp.snippet.keras.distribution import DiagonalGaussian
from tests.utils import big_number_verify


class DistributionTestCase(unittest.TestCase):
    """Distribution test cases."""

    N_SAMPLES = 10000

    def get_samples(self, distribution, kwargs, n_samples=N_SAMPLES,
                    sample_shape=(), explicit_batch_size=False):
        try:
            batch_size = n_samples if explicit_batch_size else None
            kwargs_ph = {
                k: Input(batch_shape=(batch_size,) + a.shape)
                for k, a in six.iteritems(kwargs)
            }
            keys = sorted(six.iterkeys(kwargs))
            output = distribution(**kwargs_ph).sample(sample_shape=sample_shape)
            function = K.function([kwargs_ph[k] for k in keys], [output])
            return function(
                [np.asarray([kwargs[k]] * n_samples, dtype=K.floatx())
                 for k in keys]
            )[0]
        except Exception:
            getLogger(__name__).exception(
                'failed to get samples for %r' %
                ((distribution, kwargs, n_samples, sample_shape,
                  explicit_batch_size),)
            )
            raise

    def test_diagonal_gaussian(self):
        mu = np.asarray([0.0, 1.0, -2.0])
        var = np.asarray([1.0, 2.0, 5.0])

        # test 2d sampling
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'var': var})
        self.assertEquals(samples.shape, (self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples, axis=0), mu, np.sqrt(var),
                          self.N_SAMPLES)

        # test 2d sampling (explicit batch size)
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'var': var},
                                   explicit_batch_size=True)
        self.assertEquals(samples.shape, (self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples, axis=0), mu, np.sqrt(var),
                          self.N_SAMPLES)

        # test extra sampling shape
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'var': var},
                                   sample_shape=[4, 5])
        self.assertEquals(samples.shape, (4, 5, self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples.reshape([-1, 3]), axis=0),
                          mu, np.sqrt(var), self.N_SAMPLES)

        # test extra sampling shape == 1
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'var': var},
                                   sample_shape=[1])
        self.assertEquals(samples.shape, (1, self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples.reshape([-1, 3]), axis=0), mu,
                          np.sqrt(var), self.N_SAMPLES)

        # test 3d sampling
        bias = [[0.0], [3.0], [6.0], [9.0]]
        samples = self.get_samples(
            DiagonalGaussian,
            {
                'mu': mu.reshape([1, 3]) + bias,
                'var': mu.reshape([1, 3]) + bias
            }
        )
        self.assertEquals(samples.shape, (self.N_SAMPLES, 4, 3))
        for i in range(4):
            big_number_verify(
                np.mean(samples[:, i, :], axis=0), mu + bias[i],
                np.sqrt(var + bias[i]), self.N_SAMPLES
            )

        # test log sampling
        samples = self.get_samples(
            DiagonalGaussian, {'mu': mu, 'log_var': np.log(var)})
        self.assertEquals(samples.shape, (self.N_SAMPLES, 3))
        big_number_verify(
            np.mean(samples, axis=0), mu, np.sqrt(var), self.N_SAMPLES)
