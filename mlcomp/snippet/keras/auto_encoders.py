# -*- coding: utf-8 -*-
from keras.engine import Layer, Model
from keras.layers import Lambda
from keras.models import Sequential
from tensorflow.contrib.distributions import Distribution, six

__all__ = ['AutoEncoder']


class AutoEncoder(Model):
    """Basic auto-encoder.

    Parameters
    ----------
    input : Layer | list[Layer]
        Input layer(s) to this auto-encoder.

    encoder : Layer | list[Layer]
        A layer or a sequential of layers, as the encoder network.

    decoder : Layer | list[Layer]
        A layer or a sequential of layers, as the decoder network.

    regularizer_losses : list[tensor]
        Additional list of regularizers to be applied to objective function.

    name : str
        Name of this auto-encoder.
    """

    def __init__(self, input, encoder, decoder, regularizer_losses=None,
                 name=None):
        # check the arguments
        if isinstance(encoder, (tuple, list)):
            encoder = Sequential(encoder, name='encoder')
        elif not isinstance(encoder, Layer):
            raise TypeError('`encoder` is expected to be a layer or a '
                            'sequential of layers.')
        if isinstance(decoder, (tuple, list)):
            decoder = Sequential(decoder, name='decoder')
        elif not isinstance(decoder, Layer):
            raise TypeError('`decoder` is expected to be a layer or a '
                            'sequential of layers.')
        self._encoder = encoder
        self._decoder = decoder
        if regularizer_losses:
            self._regularizer_losses = list(regularizer_losses)
        else:
            self._regularizer_losses = None

        # now build the model immediately
        self.encoder_output = encoder(input)
        self.decoder_output = decoder(self.encoder_output)
        super(AutoEncoder, self).__init__(
            input=input, output=self.decoder_output, name=name)

    def get_encoder(self, input):
        """Get the encoder model for the specified input."""
        return Model(input, self._encoder(input))

    def get_decoder(self, input):
        """Get the decoder model for the specified input."""
        return Model(input, self._decoder(input))

    @property
    def losses(self):
        ret = super(AutoEncoder, self).losses
        if self._regularizer_losses:
            ret += self._regularizer_losses
        return ret


class GaussianLatentVAE(AutoEncoder):
    """Base class for VAE with diagonal gaussian latent distribution.

    Parameters
    ----------
    input : Layer | list[Layer]
        Input layer(s) to this auto-encoder.

    encoder_param : Layer | list[Layer]
        A layer or a sequential of layers, which produces the mean and
        log-covariance of the latent gaussian distribution.

    decoder : Layer | list[Layer]
        A layer or a sequential of layers, as the decoder network.

    regularizer_losses : list[tensor]
        Additional list of regularizers to be applied to objective function.

    name : str
        Name of this auto-encoder.
    """

    def __init__(self, input, encoder_param, decoder, regularizer_losses=None,
                 name=None):
        # derive the latent distribution and variable
        self._encoder_param = encoder_param

        super(GaussianLatentVAE, self).__init__(
            input, encoder, decoder, regularizer_losses=regularizer_losses,
            name=name
        )


class BinomialVAE(AutoEncoder):
    """Variational auto-encoder with binomial output.

    Parameters
    ----------
    input : Layer | list[Layer]
        Input layer(s) to this auto-encoder.

    encoder_param : Layer | list[Layer]


    regularizer_losses : list[tensor]
        Additional list of regularizers to be applied to objective function.

    name : str
        Name of this auto-encoder.
    """
