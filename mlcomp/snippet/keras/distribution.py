# -*- coding: utf-8 -*-
from __future__ import absolute_import

import math
from keras import backend as K

from .utils import get_shape, is_deterministic_shape, reshape_tensor

__all__ = ['Distribution', 'DiagonalGaussian']


class Distribution(object):
    """Base class for various distributions."""

    def sample(self, sample_shape=()):
        """Sample from the distribution.

        Parameters
        ----------
        sample_shape : tuple[int | tensor]
            The shape of the samples.

        Returns
        -------
        tensor
        """
        raise NotImplementedError()

    def likelihood(self, x):
        """Compute the likelihood of `x` against the distribution.

        The extra dimensions at the front of `x` will be regarded as
        different samples, and the likelihood will be computed along
        these dimensions.

        Parameters
        ----------
        x : tensor
            The samples of the distribution.

        Returns
        -------
        tensor
            The likelihood of `x`.
        """
        raise NotImplementedError()

    def log_likelihood(self, x):
        """Compute the log-likelihood of `x` against the distribution.

        Parameters
        ----------
        x : tensor
            The samples of the distribution.

        Returns
        -------
        tensor
            The log-likelihood of `x`.
        """
        raise NotImplementedError()


class DiagonalGaussian(Distribution):
    """Diagonal gaussian distribution.

    Parameters
    ----------
    mu : tensor
        The mean of the gaussian distribution.
        Auxiliary dimensions will be treated as sample shape.

    stddev : tensor
        The standard derivation of the gaussian distribution.
        Auxiliary dimensions will be treated as sample shape.
    """

    def __init__(self, mu, stddev):
        # we require the shape information of `mu` and `var` to be available,
        # otherwise we shall not determine the sample shape under Theano.
        mu_shape = get_shape(mu)
        stddev_shape = get_shape(stddev)
        if not isinstance(mu_shape, tuple) or \
                not isinstance(stddev_shape, tuple):
            raise ValueError('At least the dimension of `mu` and `stddev` '
                             'should be deterministic.')

        # check whether or not mu / stddev need reshape
        pad_size = len(mu_shape) - len(stddev_shape)
        if pad_size < 0:
            mu_shape = (1,) * (-pad_size) + mu_shape
        elif pad_size > 0:
            stddev_shape = (1,) * pad_size + stddev_shape

        # compute the sample shape from mu_shape and stddev_shape
        sample_shape = [1] * len(mu_shape)
        for i in range(len(sample_shape)):
            a, b = mu_shape[i], stddev_shape[i]
            a_deterministic = is_deterministic_shape([a])
            b_deterministic = is_deterministic_shape([b])
            if a_deterministic and b_deterministic:
                if a != b and a != 1 and b != 1:
                    raise ValueError('Mismatch shape of `mu` and `stddev`.')
                sample_shape[i] = max(a, b)
            elif a_deterministic or b_deterministic:
                raise ValueError(
                    'Shape of `mu` and `stddev` must be both deterministic '
                    'or neither deterministic at corresponding dimension.'
                )
            else:
                # select the dynamic shape of either one
                sample_shape[i] = a

        self._sample_shape = tuple(sample_shape)
        self._mu = mu
        self._stddev = stddev

    def _expand_param_dims(self, k):
        """Get `mu` and `stddev` which has `k` dimensions."""
        mu, stddev = self._mu, self._stddev
        mu_shape = get_shape(mu)
        stddev_shape = get_shape(stddev)
        if len(mu_shape) < k:
            mu = reshape_tensor(mu, (1,) * (k - len(mu_shape)) + mu_shape)
        if len(stddev_shape) < k:
            stddev = reshape_tensor(
                stddev, (1,) * (k - len(stddev_shape)) + stddev_shape)
        return mu, stddev

    def _prepare_params_for_elem_op(self, x):
        """Prepare parameters for element-wise operation against `x`."""
        x_shape = get_shape(x)
        if not isinstance(x_shape, (tuple, list)):
            raise TypeError(
                'The dimension of `x` must be deterministic.')
        if len(x_shape) < len(self._sample_shape):
            raise TypeError(
                'The dimension of `x` must be at least the same as '
                'the distribution parameters.'
            )
        mu, stddev = self._expand_param_dims(len(x_shape))
        return mu, stddev

    def sample(self, sample_shape=()):
        # determine the sample shape
        if not isinstance(sample_shape, (tuple, list)):
            raise TypeError(
                'The dimension of `sample_shape` must be deterministic.')

        if sample_shape:
            sample_shape = tuple(sample_shape) + self._sample_shape
        else:
            sample_shape = self._sample_shape

        # get the distribution parameters
        mu, stddev = self._expand_param_dims(len(sample_shape))

        # sample the values
        dtype = mu.dtype
        sample = K.random_normal(sample_shape, mean=0.0, stddev=1.0,
                                 dtype=dtype)
        ret = mu + sample * stddev
        return ret

    def likelihood(self, x):
        # compose p(x), which should be:
        #   exp{-1/2 * dot[(x-mu)^T,var^{-1},(x-mu)]} / sqrt{(2pi)^k * det(var)}
        mu, stddev = self._prepare_params_for_elem_op(x)
        var = K.square(stddev)
        n_dim = self._sample_shape[-1]
        if is_deterministic_shape([n_dim]):
            factor = 1. / ((2 * math.pi) ** (n_dim * 0.5))
        else:
            factor = 1. / K.pow(2 * math.pi, n_dim * 0.5)
        return factor * (
            K.exp(-0.5 * K.sum(K.square(x - mu) / var, axis=-1)) /
            K.sqrt(K.prod(var, axis=-1))
        )

    def log_likelihood(self, x):
        # compose log p(x), which should be:
        #   -1/2 * {dot[(x-mu)^T,var^{-1},(x-mu)] + k*log(2pi) + log[det(var)]}
        mu, stddev = self._prepare_params_for_elem_op(x)
        var = K.square(stddev)
        log_var = 2. * K.log(stddev)
        return -0.5 * K.sum(
            K.square(x - mu) / var + math.log(math.pi * 2) + log_var,
            axis=-1
        )
