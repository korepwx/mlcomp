# -*- coding: utf-8 -*-
from __future__ import absolute_import

from keras.engine import Layer

from .distribution import Distribution, DiagonalGaussian

__all__ = ['SamplingLayer', 'DiagonalGaussianLayer']


class SamplingLayer(Layer):
    """Base class for sampling layers.

    A sampling layer should take the input tensor(s) as parameters of
    some distribution, then sample batch of tensors from that distribution
    as the output tensors.

    The sampling layers in this package are designed to be differentiable,
    so we would prefer to use reparameterization trick to do sampling.
    """

    def get_distribution(self, inputs, **kwargs):
        """Get the distribution object for specified inputs.

        Parameters
        ----------
        inputs : tensor(s) or layer(s)
            The tensors or layers, as the parameters of the distribution.

        **kwargs
            Other arguments for constructing the distribution.

        Returns
        -------
        Distribution
        """
        raise NotImplementedError()

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

    def call(self, inputs):
        return self.get_distribution(inputs).sample()


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
    mu : tensor
        Tensor of shape (?, output_dim).

    log_var : tensor
        Tensor of shape (?, output_dim).
    """

    def __init__(self, output_dim, **kwargs):
        self.output_dim = output_dim
        super(DiagonalGaussianLayer, self).__init__(**kwargs)

    def get_distribution(self, inputs, **kwargs):
        mu, log_var = inputs
        return DiagonalGaussian(mu=mu, log_var=log_var)

    def get_output_shape_for(self, input_shape):
        output_shape = (self.output_dim,)
        self.check_input_shape(input_shape, [output_shape, output_shape])
        return input_shape[0][:1] + output_shape

    def build(self, input_shape):
        output_shape = (self.output_dim,)
        self.check_input_shape(input_shape, [output_shape, output_shape])
        super(DiagonalGaussianLayer, self).build(input_shape)
