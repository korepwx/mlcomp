# -*- coding: utf-8 -*-
from __future__ import absolute_import

import numpy as np
import six
from keras import backend as K

__all__ = ['get_shape', 'is_deterministic_shape', 'reshape_tensor']


def get_shape(x):
    """Get the shape of the specified array or tensor.

    Parameters
    ----------
    x : np.ndarray | tensor
        The array or tensor whose shape should be detected.

    Returns
    -------
    tuple[int] | tensor
        Returns a tuple of integer or tensor if at least the dimension
        of the shape can be determined.  Otherwise returns tensor as shape.
    """
    if isinstance(x, np.ndarray):
        shape = x.shape
    else:
        try:
            shape = K.int_shape(x)
            if any(s is None for s in shape):
                shape = list(shape)
                symbolic_shape = K.shape(x)
                for i in range(len(shape)):
                    if shape[i] is None:
                        shape[i] = symbolic_shape[i]
                shape = tuple(shape)
        except AttributeError:
            shape = K.shape(x)
    return shape


def is_deterministic_shape(shape):
    """Check whether or not `shape` is deterministic."""
    return (
        isinstance(shape, (tuple, list)) and
        all(isinstance(s, six.integer_types + (np.integer,)) for s in shape)
    )


def reshape_tensor(x, shape):
    """Reshape an array or a tensor.

    Parameters
    ----------
    x : np.ndarray | tensor
        The array or tensor to be reshaped.

    shape : tuple[int] | tensor
        The desired shape.

    Returns
    -------
    np.ndarray | tensor
        If `x` is a numpy array and the shape is deterministic,
        returns the reshaped array.  Otherwise returns a reshaped
        tensor.
    """
    if isinstance(x, np.ndarray) and is_deterministic_shape(shape):
        return x.reshape(shape)
    return K.reshape(x, shape)
