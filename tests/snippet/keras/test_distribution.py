# -*- coding: utf-8 -*-
import math
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
                k: Input(batch_shape=(batch_size,) + a.shape, dtype=a.dtype)
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

    def compute_likelihood(self, samples, distribution, kwargs):
        try:
            kwargs_ph = {
                k: Input(batch_shape=a.shape, dtype=a.dtype)
                for k, a in six.iteritems(kwargs)
            }
            x = Input(batch_shape=samples.shape, dtype=samples.dtype)
            keys = sorted(six.iterkeys(kwargs))
            dist = distribution(**kwargs_ph)
            outputs = dist.likelihood(x), dist.log_likelihood(x)
            function = K.function([x] + [kwargs_ph[k] for k in keys], outputs)
            return np.asarray(function(
                [samples] +
                [np.asarray(kwargs[k], dtype=K.floatx()) for k in keys]
            ))
        except Exception:
            getLogger(__name__).exception(
                'failed to compute likelihood for %r' %
                ((samples, distribution, kwargs),)
            )
            raise

    def test_diagonal_gaussian(self):
        rtol = 1e-3
        atol = 1e-5
        mu = np.asarray([0.0, 1.0, -2.0])
        std = np.asarray([1.0, 2.0, 5.0])

        def compute_likelihood(x, mu, std):
            pad_shape = (1,) * (len(x.shape) - len(mu.shape))
            x_mu = mu.reshape(pad_shape + mu.shape)
            x_std = std.reshape(pad_shape + std.shape)
            x_var = x_std ** 2
            x_logvar = np.log(x_var)
            likelihood = (
                np.exp(-0.5 * np.sum((x - x_mu) ** 2 / x_var, axis=-1)) /
                np.sqrt(np.prod(x_var, axis=-1) * (2 * math.pi) ** mu.shape[-1])
            )
            log_likelihood = -0.5 * np.sum(
                (x - x_mu) ** 2 / x_var + math.log(math.pi * 2) + x_logvar,
                axis=-1
            )
            return np.asarray([
                K.cast_to_floatx(likelihood),
                K.cast_to_floatx(log_likelihood)
            ])

        # test 2d sampling
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'stddev': std})
        self.assertEqual(samples.shape, (self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples, axis=0), mu, std, self.N_SAMPLES)
        np.testing.assert_allclose(
            self.compute_likelihood(samples, DiagonalGaussian,
                                    {'mu': mu, 'stddev': std}),
            compute_likelihood(samples, mu, std),
            rtol=rtol, atol=atol
        )

        # test 2d sampling (explicit batch size)
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'stddev': std},
                                   explicit_batch_size=True)
        self.assertEqual(samples.shape, (self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples, axis=0), mu, std, self.N_SAMPLES)

        # test extra sampling shape
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'stddev': std},
                                   sample_shape=[4, 5])
        self.assertEqual(samples.shape, (4, 5, self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples.reshape([-1, 3]), axis=0),
                          mu, std, self.N_SAMPLES)
        np.testing.assert_allclose(
            self.compute_likelihood(samples, DiagonalGaussian,
                                    {'mu': mu, 'stddev': std}),
            compute_likelihood(samples, mu, std),
            rtol=rtol, atol=atol
        )

        # test extra sampling shape == 1
        samples = self.get_samples(DiagonalGaussian, {'mu': mu, 'stddev': std},
                                   sample_shape=[1])
        self.assertEqual(samples.shape, (1, self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples.reshape([-1, 3]), axis=0), mu,
                          std, self.N_SAMPLES)
        np.testing.assert_allclose(
            self.compute_likelihood(samples, DiagonalGaussian,
                                    {'mu': mu, 'stddev': std}),
            compute_likelihood(samples, mu, std),
            rtol=rtol, atol=atol
        )

        # test 3d sampling
        bias = [[0.0], [3.0], [6.0], [9.0]]
        mu_3d = mu.reshape([1, 3]) + bias
        std_3d = std.reshape([1, 3]) + bias
        samples = self.get_samples(
            DiagonalGaussian,
            {'mu': mu_3d, 'stddev': std_3d}
        )
        self.assertEqual(samples.shape, (self.N_SAMPLES, 4, 3))
        for i in range(4):
            big_number_verify(
                np.mean(samples[:, i, :], axis=0), mu + bias[i],
                std + bias[i], self.N_SAMPLES
            )
        np.testing.assert_allclose(
            self.compute_likelihood(
                samples, DiagonalGaussian,
                {'mu': mu_3d, 'stddev': std_3d}
            ),
            compute_likelihood(samples, mu_3d, std_3d),
            rtol=rtol, atol=atol
        )

        # test log sampling
        samples = self.get_samples(
            DiagonalGaussian, {'mu': mu, 'stddev': np.log(std)})
        self.assertEqual(samples.shape, (self.N_SAMPLES, 3))
        big_number_verify(np.mean(samples, axis=0), mu, std, self.N_SAMPLES)
        np.testing.assert_allclose(
            self.compute_likelihood(samples, DiagonalGaussian,
                                    {'mu': mu, 'stddev': std}),
            compute_likelihood(samples, mu, std),
            rtol=rtol, atol=atol
        )
