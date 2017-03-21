# -*- coding: utf-8 -*-
from __future__ import absolute_import

import warnings

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
    diagonal gaussian distribution, and the mean and standard derivation
    of the latent variable is produced by a network consuming the whole
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
        The hidden layer before computing mean(z) and stddev(z).

    x_feature_layer : Layer | (tensor) -> tensor
        The hidden layer before computing output distribution parameters.

    stddev_activation : str | activation
        The activation function used for producing the standard derivation,
        if `z_mu_layer` and `z_stddev_layer` is not provided.

    z_mu_layer, z_stddev_layer : Layer | (tensor) -> tensor
        The distribution parameter layers for `z`.
    """

    def __init__(self, inputs, z_dim, z_feature_layer, x_feature_layer,
                 stddev_activation='softplus', z_mu_layer=None,
                 z_stddev_layer=None):
        if isinstance(inputs, (tuple, list)):
            self.input_x = inputs[0]
        else:
            self.input_x = inputs
        self.z_dim = z_dim
        self.stddev_activation = stddev_activation

        # build the layers to translate input frame to latent variable
        if z_mu_layer is None:
            z_mu_layer = Dense(z_dim)
        if z_stddev_layer is None:
            z_stddev_layer = Dense(z_dim, activation=stddev_activation)
        self.z_feature_layer = z_feature_layer
        self.z_mu_layer = z_mu_layer
        self.z_stddev_layer = z_stddev_layer
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
        return [self.z_mu_layer(feature), self.z_stddev_layer(feature)]

    def sample_z_for(self, x):
        """Sample `z` from `x`."""
        return self.z_sampler(self.z_params_for(x))

    def z_kl_divergence_for(self, z_params):
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
        #   -1/2 * {tr(z_var) + dot(z_mu^T,z_mu) - dim(z) - log[det(z_var)]}
        z_mu, z_stddev = z_params
        z_var = K.square(z_stddev)
        z_logvar = 2. * K.log(z_stddev)
        kld = -0.5 * K.sum(z_var + K.square(z_mu) - 1 - z_logvar, axis=-1)
        return kld

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

    def reconstructed_apply(self, input_x, func, z_sample_num=32,
                            aggregate='average'):
        """
        Feed `input_x` into the encoder and decoder, then apply `func`.

        Parameters
        ----------
        input_x : tensor
            The input tensor.

        func : (tensor, tensor, list[tensor]) -> tensor | list[tensor]
            A function that maps (input_x, z_params, z_samples, x_params)
            to a tensor or a list of tensors.  The `z_samples` will be
            `z_mu` if `z_sample_num` is None.

            Note that `input_x` and `z_params` will not match the shape of
            `z_samples`, if `z_sample_num` > 1.

        z_sample_num : int | None
            Number of `z` samples to take.

            If None is specified, use the mean of `z` instead of sampling.
            Otherwise will increase the number of `x` samples.

            Note that it is often not suitable for taking the average of `z`.
            Use enough number of `z` samples whenever possible.

        aggregate : {'average'}
            Since `z_samples` are sampled for multiple times from each
            set of parameters, the outputs produced by `func` should be
            aggregated within each group of `z_samples`.

            This argument thus determines the way to aggregate the outputs.

        Returns
        -------
        tensor
            The output tensor(s).
        """
        aggregate_methods = {
            'average': lambda o: K.mean(o, axis=0, keepdims=False)
        }
        agg_method = aggregate_methods[aggregate]
        x_shape = get_shape(input_x)
        if not is_deterministic_shape(x_shape[1:]) or len(x_shape) != 2:
            raise ValueError(
                'Input is expected to be 2D, with a deterministic '
                '2nd dimension, but got shape %r.' % x_shape
            )

        # construct the output which support Model(outputs=...)
        def compute(x):
            # take z samples or the mean of z
            z_params = self.z_params_for(x)
            if z_sample_num is None:
                z_samples = z_params[0]
            else:
                z_dist = self.z_sampler.get_distribution(z_params)
                z_samples = z_dist.sample(sample_shape=(z_sample_num,))
                z_samples = K.reshape(z_samples, [-1, self.z_dim])

            # compute the parameters of `x` given specified `z`.
            x_params = self.x_params_for(z_samples)
            outputs = func(input_x, z_params, z_samples, x_params)

            if z_sample_num is not None and z_sample_num > 1:
                def agg(output):
                    o_shape = get_shape(output)
                    if not isinstance(o_shape, (tuple, list)):
                        raise TypeError(
                            'At least the dimension of output should '
                            'be deterministic.'
                        )
                    o_shape_new = (z_sample_num, -1) + o_shape[1:]
                    if not is_deterministic_shape(o_shape_new):
                        o_shape_new = K.stack(o_shape_new)
                    return agg_method(K.reshape(output, o_shape_new))
            else:
                def agg(output):
                    return output

            if isinstance(outputs, (tuple, list)):
                outputs = [agg(o) for o in outputs]
            else:
                outputs = agg(outputs)
            return outputs

        return Lambda(compute)(input_x)

    def get_reconstructed(self, input_x, z_sample_num=32, sample_x=True):
        """Get the reconstructed tensor.

        Parameters
        ----------
        input_x : tensor
            The input layer or tensor.

        z_sample_num : int | None
            Number of `z` samples to take.

            If None is specified, use the mean of `z` instead of sampling.
            Otherwise will increase the number of `x` samples.

            Note that it is often not suitable for taking the average of `z`.
            Use enough number of `z` samples whenever possible.

        sample_x : bool
            If True, sample `x` from the distribution parameters.
            Otherwise take the mean of `x` instead of sampling.

        Returns
        -------
        tensor
            The reconstructed tensor.
        """
        if sample_x:
            def func(input_x, z_params, z_samples, x_params):
                return self.x_sampler.get_distribution(x_params).sample()
        else:
            def func(input_x, z_params, z_samples, x_params):
                return x_params[0]

        return self.reconstructed_apply(
            input_x,
            func=func,
            z_sample_num=z_sample_num
        )

    def get_reconstructed_params(self, input_x, z_sample_num=32):
        """Get the reconstructed distribution parameters.

        This method should give the most reasonable distribution parameters
        for reconstructed `x`.  Due to the existence of variational bias,
        the likelihood computed from the distribution parameters need not
        be exactly the same as `get_reconstruction_likelihood`.

        Parameters
        ----------
        input_x : tensor
            The input layer or tensor.

        z_sample_num : int | None
            Number of `z` samples to take.

            If None is specified, use the mean of `z` instead of sampling.
            Otherwise will increase the number of `x` samples.

            Note that it is often not suitable for taking the average of `z`.
            Use enough number of `z` samples whenever possible.

        Returns
        -------
        list[tensor]
            The reconstruction parameters.
        """
        raise NotImplementedError()

    def get_reconstructed_log_likelihood(self, input_x, z_sample_num=32,
                                         kl_divergence=True):
        """Get the reconstructed likelihood of `x`.

        Parameters
        ----------
        input_x : tensor
            The input layer or tensor.

        z_sample_num : int | None
            Number of `z` samples to take.

            If None is specified, use the mean of `z` instead of sampling.
            Otherwise will increase the number of `x` samples.

            Note that it is often not suitable for taking the average of `z`.
            Use enough number of `z` samples whenever possible.

        kl_divergence : bool
            Whether or not to include the KL-divergence term for likelihood?

        Returns
        -------
        tensor
            The reconstructed likelihood of `x`.
        """
        def compute(x):
            def func(input_x, z_params, z_samples, x_params):
                x_dist = self.x_sampler.get_distribution(x_params)
                if z_sample_num is not None and z_sample_num > 1:
                    x_tiled = K.repeat_elements(input_x, z_sample_num, axis=0)
                else:
                    x_tiled = input_x
                z_params_saved.append(z_params)
                return x_dist.log_likelihood(x_tiled)

            z_params_saved = []
            ret = self.reconstructed_apply(
                x,
                func=func,
                z_sample_num=z_sample_num
            )
            if kl_divergence:
                kld = self.z_kl_divergence_for(z_params_saved[0])
                ret -= kld
            return ret
        return Lambda(compute)(input_x)

    @deprecated('use `get_reconstructed` instead.')
    def sampling_reconstruct(self, *args, **kwargs):
        if 'x_sample_num' in kwargs:
            kwargs.setdefault('sample_x', kwargs.pop('x_sample_num') == 1)
            warnings.warn(
                '`x_sample_num` is deprecated. '
                'Use `sample_x = True` for `x_sample_num = 1`, '
                'and `sample_x = False` for `x_sample_num > 1`.',
                category=DeprecationWarning
            )
        return self.get_reconstructed(*args, **kwargs)

    def compile(self, optimizer, metrics=None, loss_weights=None,
                sample_weight_mode=None, **kwargs):
        def vae_loss(x, x_sampled):
            x_dist = self.x_sampler.get_distribution(self.x_params)
            return -(
                x_dist.log_likelihood(x) +
                self.z_kl_divergence_for(self.z_params)
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
        The hidden layer before computing mean(z) and stddev(z).

    x_feature_layer : Layer | (tensor) -> tensor
        The hidden layer before computing mean(x) and stddev(x).

    stddev_activation : str | activation
        The activation function used for producing the standard derivation,
        given input feature vector.

    z_mu_layer, z_stddev_layer : Layer | (tensor) -> tensor
        The distribution parameter layers for `z`.

    x_mu_layer, x_stddev_layer : Layer | (tensor) -> tensor
        The distribution parameter layers for `x`.
    """

    def __init__(self, inputs, z_dim, z_feature_layer, x_feature_layer,
                 stddev_activation='softplus', z_mu_layer=None,
                 z_stddev_layer=None, x_mu_layer=None,
                 x_stddev_layer=None):
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
        self.x_mu_layer = x_mu_layer
        self.x_stddev_layer = x_stddev_layer

        # call the standard VAE constructor
        super(DiagonalGaussianSimpleVAE, self).__init__(
            inputs=inputs,
            z_dim=z_dim,
            z_feature_layer=z_feature_layer,
            x_feature_layer=x_feature_layer,
            stddev_activation=stddev_activation,
            z_mu_layer=z_mu_layer,
            z_stddev_layer=z_stddev_layer,
        )

    def _build_x_layers(self):
        activation = self.stddev_activation
        if self.x_mu_layer is None:
            self.x_mu_layer = Dense(self.x_dim)
        if self.x_stddev_layer is None:
            self.x_stddev_layer = Dense(self.x_dim, activation=activation)
        self._x_sampler = DiagonalGaussianLayer(self.x_dim)

    @property
    def x_sampler(self):
        return self._x_sampler

    def x_params_for(self, z):
        feature = self.x_feature_layer(z)
        return [self.x_mu_layer(feature), self.x_stddev_layer(feature)]

    def get_reconstructed_params(self, input_x, z_sample_num=32):
        """Get `mu`, `stddev` and `var` of reconstructed `x`."""
        def compute(x):
            def func(input_x, z_params, z_samples, x_params):
                x_mu, x_std = x_params
                return [
                    # the expectation term
                    x_mu,
                    # the first term of variance
                    K.square(x_std) + K.square(x_mu),
                ]

            mu, var_left = self.reconstructed_apply(
                x,
                func=func,
                z_sample_num=z_sample_num
            )
            var = var_left - K.square(mu)
            return [mu, K.sqrt(var), var]
        return Lambda(compute)(input_x)
