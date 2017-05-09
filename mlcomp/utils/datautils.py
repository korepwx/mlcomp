# -*- coding: utf-8 -*-
import numpy as np

__all__ = [
    'minibatch_slices_iterator', 'minibatch_iterator', 'split_numpy_arrays',
    'split_numpy_array',
]


def minibatch_slices_iterator(length, batch_size,
                              ignore_incomplete_batch=False):
    """Iterate through all the mini-batch slices.

    Parameters
    ----------
    length : int
        Total length of data in an epoch.

    batch_size : int
        Size of each mini-batch.

    ignore_incomplete_batch : bool
        Whether or not to ignore the final batch if it contains less
        than ``batch-size`` number of items?  (default False)

    Yields
    ------
    slice
        Slices of each mini-batch.  The last mini-batch may contain less
        indices than `batch_size`.
    """
    start = 0
    stop1 = (length // batch_size) * batch_size
    while start < stop1:
        yield slice(start, start + batch_size, 1)
        start += batch_size
    if not ignore_incomplete_batch and start < length:
        yield slice(start, length, 1)


def minibatch_iterator(array, batch_size, ignore_incomplete_batch=False):
    """Iterate through all the mini-batches.

    Parameters
    ----------
    array
        List or numpy array, or any object that supports slicing.

    batch_size : int
        Size of each mini-batch.

    ignore_incomplete_batch : bool
        Whether or not to ignore the final batch if it contains less
        than ``batch-size`` number of items?  (default False)

    Yields
    ------
    sliced array
        Sliced array of each mini-batch.  The last mini-batch may contain
        less elements than `batch_size`.
    """
    for s in minibatch_slices_iterator(len(array), batch_size,
                                       ignore_incomplete_batch):
        yield array[s]


def split_numpy_arrays(arrays, portion=None, size=None, shuffle=True):
    """Split NumPy arrays into two halves, by portion or by size.

    Parameters
    ----------
    arrays : collections.Iterable[np.ndarray]
        A collection of NumPy arrays to be splitted.

    portion : float
        Portion of the second half.  Ignored if `size` is specified.

    size : int
        Size of the second half.

    shuffle : bool
        Whether or not to shuffle before splitting?

    Returns
    -------
    (tuple[np.ndarray], tuple[np.ndarray])
        Splitted two halves of arrays.
    """
    # check the arguments
    if size is None and portion is None:
        raise ValueError('At least one of `portion` and `size` should '
                         'be specified.')

    # zero arrays should return empty tuples
    arrays = tuple(arrays)
    if not arrays:
        return (), ()

    # check the length of provided arrays
    data_count = len(arrays[0])
    for array in arrays[1:]:
        if len(array) != data_count:
            raise ValueError('The length of specified arrays are not equal.')

    # determine the size for second half
    if size is None:
        if portion < 0.0 or portion > 1.0:
            raise ValueError('`portion` must range from 0.0 to 1.0.')
        elif portion < 0.5:
            size = data_count - int(data_count * (1.0 - portion))
        else:
            size = int(data_count * portion)

    # shuffle the data if necessary
    if shuffle:
        indices = np.arange(data_count)
        np.random.shuffle(indices)
        arrays = tuple(a[indices] for a in arrays)

    # return directly if each side remains no data after splitting
    if size <= 0:
        return arrays, tuple(a[:0] for a in arrays)
    elif size >= data_count:
        return tuple(a[:0] for a in arrays), arrays

    # split the data according to demand
    return (
        tuple(v[: -size, ...] for v in arrays),
        tuple(v[-size:, ...] for v in arrays)
    )


def split_numpy_array(array, portion=None, size=None, shuffle=True):
    """Split NumPy array into two halves, by portion or by size.

    Parameters
    ----------
    array : np.ndarray
        A NumPy array to be splitted.

    portion : float
        Portion of the second half.  Ignored if `size` is specified.

    size : int
        Size of the second half.

    shuffle : bool
        Whether or not to shuffle before splitting?

    Returns
    -------
    tuple[np.ndarray]
        Splitted two halves of array.
    """
    (a,), (b,) = split_numpy_arrays((array,), portion=portion, size=size,
                                    shuffle=shuffle)
    return a, b
