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
        The mean and the log variance of the gaussian distribution.
        Auxiliary dimensions will be treated as sample shape.

    var, log_var : tensor
        The variance or the log variance of the gaussian distribution,
        while either one and only one should be specified.

        Auxiliary dimensions will be treated as sample shape.
        The shape of the variance or log-variance must match `mu`.
    """

    def __init__(self, mu, var=None, log_var=None):
        if (var is None and log_var is None) or \
                (var is not None and log_var is not None):
            raise ValueError('Either one and only one of `var`, `log_var` '
                             'should be specified.')

        # we require the shape information of `mu` and `var` to be available,
        # otherwise we shall not determine the sample shape under Theano.
        mu_shape = get_shape(mu)
        if var is not None:
            var_x = var
        else:
            var_x = log_var
        var_x_shape = get_shape(var_x)
        if not isinstance(mu_shape, tuple) or \
                not isinstance(var_x_shape, tuple):
            raise ValueError('At least the dimension of `mu`, `var` and '
                             '`log_var` should be deterministic.')

        # check whether or not mu / var_x need reshape
        pad_size = len(mu_shape) - len(var_x_shape)
        if pad_size < 0:
            mu_shape = (1,) * (-pad_size) + mu_shape
        elif pad_size > 0:
            var_x_shape = (1,) * pad_size + var_x_shape

        # compute the sample shape from mu_shape and var_x_shape
        sample_shape = [1] * len(mu_shape)
        for i in range(len(sample_shape)):
            a, b = mu_shape[i], var_x_shape[i]
            a_deterministic = is_deterministic_shape([a])
            b_deterministic = is_deterministic_shape([b])
            if a_deterministic and b_deterministic:
                if a != b and a != 1 and b != 1:
                    raise ValueError('Mismatch shape of mu and var.')
                sample_shape[i] = max(a, b)
            elif a_deterministic or b_deterministic:
                raise ValueError(
                    'Shape of mu and var must be both deterministic '
                    'or neither deterministic at corresponding dimension.'
                )
            else:
                # select the dynamic shape of either one
                sample_shape[i] = a

        self._sample_shape = tuple(sample_shape)
        self._mu = mu
        self._var_x = var_x
        self._is_log_var = log_var is not None

    def _expand_param_dims(self, k):
        """Get `mu` and `var_x` which has `k` dimensions."""
        mu, var_x = self._mu, self._var_x
        mu_shape = get_shape(mu)
        var_x_shape = get_shape(var_x)
        if len(mu_shape) < k:
            mu = reshape_tensor(mu, (1,) * (k - len(mu_shape)) + mu_shape)
        if len(var_x_shape) < k:
            var_x = reshape_tensor(
                var_x, (1,) * (k - len(var_x_shape)) + var_x_shape)
        return mu, var_x

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
        mu, var_x = self._expand_param_dims(len(x_shape))
        return mu, var_x

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
        mu, var_x = self._expand_param_dims(len(sample_shape))

        # sample the values
        dtype = mu.dtype
        sample = K.random_normal(sample_shape, mean=0.0, stddev=1.0,
                                 dtype=dtype)
        if self._is_log_var:
            ret = mu + sample * K.exp(var_x * 0.5)
        else:
            ret = mu + sample * K.sqrt(var_x)
        return ret

    def likelihood(self, x):
        # compose p(x), which should be:
        #   exp{-1/2 * dot[(x-mu)^T,var^{-1},(x-mu)]} / sqrt{(2pi)^k * det(var)}
        mu, var_x = self._prepare_params_for_elem_op(x)
        if self._is_log_var:
            var = K.exp(var_x)
        else:
            var = var_x
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
        mu, var_x = self._prepare_params_for_elem_op(x)
        if self._is_log_var:
            log_var = var_x
            var = K.exp(var_x)
        else:
            log_var = K.log(var_x)
            var = var_x
        return -0.5 * K.sum(
            K.square(x - mu) / var + math.log(math.pi * 2) + log_var,
            axis=-1
        )
