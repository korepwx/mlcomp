# -*- coding: utf-8 -*-
import unittest

import numpy as np
from keras import backend as K
from keras.engine import Input, Model

from mlcomp.snippet.keras.sampling import DiagonalGaussianLayer
from tests.utils import big_number_verify


class SamplingTestCase(unittest.TestCase):
    """Tests for sampling layers."""

    N_SAMPLES = 10000

    def get_samples(self, layer, args, n_samples=N_SAMPLES,
                    explicit_batch_size=False):
        batch_size = n_samples if explicit_batch_size else None
        placeholders = [
            Input(batch_shape=(batch_size,) + a.shape)
            for a in args
        ]
        output = layer(placeholders)
        model = Model(placeholders, output)
        return model.predict([
            np.asarray([a] * n_samples, dtype=K.floatx())
            for a in args
        ])

    def test_diagonal_gaussian(self):
        layer = DiagonalGaussianLayer(3)
        mean = np.asarray([0.0, 1.0, -2.0])
        covariance = np.asarray([1.0, 2.0, 5.0])
        samples = self.get_samples(
            layer,
            [mean, np.log(covariance)]
        )
        big_number_verify(np.mean(samples, axis=0), mean, np.sqrt(covariance),
                          self.N_SAMPLES)
