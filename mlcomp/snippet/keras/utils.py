# -*- coding: utf-8 -*-
from __future__ import absolute_import

from keras import backend as K


def get_batch_size(x):
    """Get the batch size of the specified tensor.

    Parameters
    ----------
    x : tensor
        The tensor whose batch size should be queried.

    Returns
    -------
    int | tensor
        Returns an integer if the tensor has a determined batch size.
        Otherwise returns a tensor.
    """
    try:
        batch_size = K.get_variable_shape(x)[0]
        if batch_size is not None:
            return batch_size
    except AttributeError:
        pass
    return K.shape(x)[0]
