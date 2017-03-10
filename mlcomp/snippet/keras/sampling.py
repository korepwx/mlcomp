# -*- coding: utf-8 -*-
from __future__ import absolute_import

import six
from keras import backend as K
from keras.engine import Layer

from .utils import get_batch_size


class SamplingLayer(Layer):
    """Base class for sampling layers.

    A sampling layer should take the input tensor(s) as parameters of
    some distribution, then sample batch of tensors from that distribution
    as the output tensors.

    The sampling layers in this package are designed to be differentiable,
    so we would prefer to use reparameterization trick to do sampling.
    """

    def check_input_shape(self, input_shape, arg_shapes):
        # first, validate the number of parameters
        if not arg_shapes:
            if input_shape:
                raise ValueError(
                    '%s expects no distribution parameter.' %
                    self.__class__.__name__
                )
            input_shape = []
        elif len(arg_shapes) == 1:
            if isinstance(input_shape, list):
                if len(input_shape) != 1:
                    raise ValueError(
                        '%s expects exactly one distribution parameter.' %
                        self.__class__.__name__
                    )
            else:
                input_shape = [input_shape]
        else:
            if not isinstance(input_shape, list) or \
                    len(arg_shapes) != len(input_shape):
                raise ValueError(
                    '%s expects exactly %d distribution parameters.' %
                    (self.__class__.__name__, len(arg_shapes))
                )

        # next, validate the shape of each parameter
        if input_shape:
            if len(set(i[0] for i in input_shape)) != 1:
                raise ValueError(
                    '%s: batch size of inputs does not agree.' %
                    self.__class__.__name__
                )
            for k, (i, a) in enumerate(zip(input_shape, arg_shapes)):
                if i[1:] != a:
                    raise ValueError(
                        '%s: parameter(%d) expects shape %r, but got %r.' %
                        (self.__class__.__name__, k, a, i[1:])
                    )


class DiagonalGaussianLayer(SamplingLayer):
    """Gaussian sampling layer with diagonal covariance.

    This layer should sample 2d gaussian variables from some diagonal
    gaussian distribution.  The mean and the log diagonal covariance
    should be fed into this layer from previous ones.

    Parameters
    ----------
    output_dim : int
        The dimension of the gaussian distribution.

    Distribution Parameters
    -----------------------
    mean : tensor
        Tensor of shape (?, output_dim).

    log_covariance : tensor
        Tensor of shape (?, output_dim).
    """

    def __init__(self, output_dim, **kwargs):
        self.output_dim = output_dim
        super(DiagonalGaussianLayer, self).__init__(**kwargs)

    def get_output_shape_for(self, input_shape):
        output_shape = (self.output_dim,)
        self.check_input_shape(input_shape, [output_shape, output_shape])
        return input_shape[0][:1] + output_shape

    def build(self, input_shape):
        output_shape = (self.output_dim,)
        self.check_input_shape(input_shape, [output_shape, output_shape])
        super(DiagonalGaussianLayer, self).build(input_shape)

    def call(self, x, mask=None):
        mean, log_covariance = x
        batch_size = get_batch_size(mean)
        if isinstance(batch_size, six.integer_types):
            shape = [batch_size, self.output_dim]
        else:
            shape = K.stack([batch_size, self.output_dim])
        sample = K.random_normal(shape, mean=0.0, std=1.0)
        return mean + K.exp(log_covariance / 2) * sample
