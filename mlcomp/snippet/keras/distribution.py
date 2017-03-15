# -*- coding: utf-8 -*-
from __future__ import absolute_import

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
        mu_reshape = var_x_reshape = False
        if pad_size < 0:
            mu_shape = (1,) * (-pad_size) + mu_shape
            mu_reshape = True
        elif pad_size > 0:
            var_x_shape = (1,) * pad_size + var_x_shape
            var_x_reshape = True

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
        self._mu_shape = mu_shape
        self._mu_reshape = mu_reshape
        self._var_x = var_x
        self._var_x_shape = var_x_shape
        self._var_x_reshape = var_x_reshape
        self._is_log_var = log_var is not None

    def sample(self, sample_shape=()):
        mu, mu_shape, mu_reshape = \
            self._mu, self._mu_shape, self._mu_reshape
        var_x, var_x_shape, var_x_reshape = \
            self._var_x, self._var_x_shape, self._var_x_reshape

        # determine the sample shape
        if not isinstance(sample_shape, (tuple, list)):
            raise TypeError(
                'The dimension of `sample_shape` must be deterministic.')

        if sample_shape:
            pad_shape = (1,) * len(sample_shape)
            sample_shape = tuple(sample_shape) + self._sample_shape
            mu_shape = pad_shape + mu_shape
            var_x_shape = pad_shape + var_x_shape
            mu_reshape = var_x_reshape = True
        else:
            sample_shape = self._sample_shape

        # reshape mu and var if necessary
        if mu_reshape:
            mu = reshape_tensor(mu, mu_shape)
        if var_x_reshape:
            var_x = reshape_tensor(var_x, var_x_shape)

        # sample the values
        dtype = mu.dtype
        sample = K.random_normal(sample_shape, mean=0.0, stddev=1.0,
                                 dtype=dtype)
        if self._is_log_var:
            ret = mu + sample * K.exp(var_x * 0.5)
        else:
            ret = mu + sample * K.sqrt(var_x)
        return ret
