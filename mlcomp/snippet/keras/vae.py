# -*- coding: utf-8 -*-
from __future__ import absolute_import

import math

from keras import backend as K
from keras.engine import Model, Layer
from keras.layers import Dense, Lambda

from mlcomp.utils import deprecated
from .sampling import DiagonalGaussianLayer
from .utils import get_shape, is_deterministic_shape

__all__ = ['SimpleVAE', 'DiagonalGaussianSimpleVAE']


class SimpleVAE(Model):
    """Basic class for simple variational auto-encoders.

    By "simple" we refer to such VAE whose latent variable follows
    diagonal gaussian distribution, and the mean and log-variance of
    the latent variable is produced by a network consuming the whole
    input vector.

    Parameters
    ----------
    inputs
        The input layer(s) or tensor(s).

        If more than one layer or tensor is specified, the first one
        will be chosen as the target tensor.

    z_dim : int
        The dimension of the latent variable.

    z_feature_layer : Layer | (tensor) -> tensor
        The hidden layer before computing mean(z) and logvar(z).

    x_feature_layer : Layer | (tensor) -> tensor
        The hidden layer before computing output distribution parameters.
    """

    def __init__(self, inputs, z_dim, z_feature_layer, x_feature_layer):
        if isinstance(inputs, (tuple, list)):
            self.input_x = inputs[0]
        else:
            self.input_x = inputs
        self.z_dim = z_dim

        # build the layers to translate input frame to latent variable
        self.z_feature_layer = z_feature_layer
        self.z_mean_layer = Dense(z_dim)
        self.z_logvar_layer = Dense(z_dim)
        self.z_sampler = DiagonalGaussianLayer(z_dim)

        # build the layers to translate latent variable back to frame
        self.x_feature_layer = x_feature_layer
        self._build_x_layers()

        # build the graph nodes
        self.z_params = self.z_params_for(self.input_x)
        self.z = self.z_sampler(self.z_params)
        self.x_params = self.x_params_for(self.z)
        self.x = self.x_sampler(self.x_params)

        # initialize the model
        super(SimpleVAE, self).__init__(inputs=inputs, outputs=self.x)

    def z_params_for(self, x):
        """Compute the distribution parameters of `z` for specified `x`.

        Parameters
        ----------
        x : tensor
            The `x` input variable.

        Returns
        -------
        list[tensor]
        """
        feature = self.z_feature_layer(x)
        return [self.z_mean_layer(feature), self.z_logvar_layer(feature)]

    def sample_z_for(self, x):
        """Sample `z` from `x`."""
        return self.z_sampler(self.z_params_for(x))

    def _build_x_layers(self):
        """Build output specified layers."""
        raise NotImplementedError()

    @property
    def x_sampler(self):
        """Get the sampling layer of `x`."""
        raise NotImplementedError()

    def x_params_for(self, z):
        """Compute the distribution parameters of `x` for specified `z`.

        The first output of this method is required to be the mean of `x`.

        Parameters
        ----------
        z : tensor
            The `z` latent variable.

        Returns
        -------
        list[tensor]
        """
        raise NotImplementedError()

    def sample_x_for(self, z):
        """Sample `x` from specified `z`."""
        return self.x_sampler(self.x_params_for(z))

    def kl_divergence_for(self, z_params):
        """Compute the variational KL-divergence.

        Parameters
        ----------
        z_params
            Distribution parameters for `z`.

        Returns
        -------
        tensor
        """
        # compose the KL-divergence, which should be:
        #   -1/2 * {tr(z_var) + dot(z_mean^T,z_mean) - dim(z) - log[det(z_var)]}
        z_mean, z_logvar = z_params
        z_var = K.exp(z_logvar)
        kld = -0.5 * K.sum(z_var + K.square(z_mean) - 1 - z_logvar, axis=-1)
        return kld

    def log_likelihood_for(self, x, x_params):
        """Compute the log-likelihood of `x` given distribution parameters.

        Parameters
        ----------
        x
            The input layer or tensor.

        x_params
            Distribution parameters for `x`.

        Returns
        -------
        tensor
        """
        raise NotImplementedError()

    def get_reconstructed(self, input_x, z_sample_num=32, x_sample_num=None):
        """Get the reconstructed tensor.

        Parameters
        ----------
        input_x : tensor
            The input layer or tensor.

        z_sample_num : int | None
            Number of `z` samples to take.

            If None is specified, use the mean of `z` instead of sampling.
            Otherwise will increase the number of `x` samples.

        x_sample_num : int | None
            Number of `x` samples to take.

            If None is specified, use the mean of `x` instead of sampling.
            Otherwise will compute the average of the sampled `x`.

        Returns
        -------
        tensor
            The reconstructed tensor.
        """
        def compute(x):
            # take z samples or the mean of z
            if z_sample_num is None:
                z_samples = self.z_params_for(x)[0]
            else:
                z_params = self.z_params_for(x)
                z_dist = self.z_sampler.get_distribution(z_params)
                z_samples = z_dist.sample(sample_shape=(z_sample_num,))
                z_samples = K.reshape(z_samples, [-1, self.z_dim])

            # take x samples or the mean of x
            if x_sample_num is None:
                x_samples = self.x_params_for(z_samples)[0]
            else:
                x_params = self.x_params_for(x)
                x_dist = self.x_sampler.get_distribution(x_params)
                x_samples = x_dist.sample(sample_shape=(x_sample_num,))

                # now take the average out the x samples
                if x_sample_num > 1:
                    x_samples = K.mean(x_samples, axis=0, keepdims=False)
                else:
                    x_samples = K.squeeze(x_samples, axis=0)

            # average out the z samples
            if z_sample_num is not None and z_sample_num > 1:
                x_samples = K.mean(
                    K.reshape(x_samples, [z_sample_num, -1, x_dim]),
                    axis=0,
                    keepdims=False
                )
            return x_samples

        x_shape = get_shape(input_x)
        if not is_deterministic_shape(x_shape[1:]) or len(x_shape) != 2:
            raise ValueError(
                'Input is expected to be 2D, with a deterministic '
                '2nd dimension, but got shape %r.' % x_shape
            )
        x_dim = x_shape[1]
        # construct the output which support Model(outputs=...)
        return Lambda(compute)(input_x)

    @deprecated('use `get_reconstructed` instead.')
    def sampling_reconstruct(self, *args, **kwargs):
        return self.get_reconstructed(*args, **kwargs)

    def compile(self, optimizer, metrics=None, loss_weights=None,
                sample_weight_mode=None, **kwargs):
        def vae_loss(x, x_sampled):
            return -(
                self.log_likelihood_for(x, self.x_params) +
                self.kl_divergence_for(self.z_params)
            )
        kwargs.setdefault('loss', vae_loss)
        return super(SimpleVAE, self).compile(
            optimizer, metrics=metrics, loss_weights=loss_weights,
            sample_weight_mode=sample_weight_mode, **kwargs
        )


class DiagonalGaussianSimpleVAE(SimpleVAE):
    """Simple variational auto-encoder with diagonal gaussian output.

    Parameters
    ----------
    inputs
        The input layer(s) or tensor(s).

    z_dim : int
        The dimension of the latent variable.

    z_feature_layer : Layer | (tensor) -> tensor
        The hidden layer before computing mean(z) and logvar(z).

    x_feature_layer : Layer | (tensor) -> tensor
        The hidden layer before computing mean(x) and logvar(x).
    """

    def __init__(self, inputs, z_dim, z_feature_layer, x_feature_layer):
        # check the arguments
        if isinstance(inputs, (tuple, list)):
            input_x = inputs[0]
        else:
            input_x = inputs
        input_shape = get_shape(input_x)
        if not is_deterministic_shape(input_shape[1:]) or len(input_shape) != 2:
            raise ValueError(
                'Input is expected to be 2D, with a deterministic '
                '2nd dimension, but got shape %r.' % input_shape
            )
        x_dim = input_shape[1]
        self.x_dim = x_dim

        # call the standard VAE constructor
        super(DiagonalGaussianSimpleVAE, self).__init__(
            inputs=inputs,
            z_dim=z_dim,
            z_feature_layer=z_feature_layer,
            x_feature_layer=x_feature_layer,
        )

    def _build_x_layers(self):
        self.x_mean_layer = Dense(self.x_dim)
        self.x_logvar_layer = Dense(self.x_dim)
        self._x_sampler = DiagonalGaussianLayer(self.x_dim)

    @property
    def x_sampler(self):
        return self._x_sampler

    def x_params_for(self, z):
        feature = self.x_feature_layer(z)
        return [self.x_mean_layer(feature), self.x_logvar_layer(feature)]

    def log_likelihood_for(self, x, x_params):
        # compose the p(x|z) likelihood loss, which should be:
        #   -1/2 * {dot[(x-x_mean)^T,x_var^{-1},(x-x_mean)] + k*log(2pi) +
        #           log[det(x_var)]}
        x_mean, x_logvar = x_params
        x_var = K.exp(x_logvar)
        log_likelihood = -0.5 * K.sum(
            K.square(x - x_mean) / x_var + math.log(math.pi * 2) + x_logvar,
            axis=-1
        )
        return log_likelihood
