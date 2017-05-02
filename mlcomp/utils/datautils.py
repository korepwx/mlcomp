# -*- coding: utf-8 -*-
import numpy as np

__all__ = [
    'minibatch_slices_iterator', 'minibatch_iterator', 'split_numpy_array',
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


def split_numpy_array(arrays, portion=None, size=None, shuffle=True):
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
    arrays = tuple(arrays)
    if not arrays:
        raise ValueError('`arrays` must not be empty.')

    # check the length of provided arrays
    data_count = len(arrays[0])
    for array in arrays[1:]:
        if len(array) != data_count:
            raise ValueError('The length of specified arrays are not equal.')

    # determine the size for second half
    if size is None:
        if portion is None:
            raise ValueError('At least one of `portion` and `size` should '
                             'be specified.')

        if portion < 0.5:
            size = data_count - int(data_count * (1.0 - portion))
        else:
            size = int(data_count * portion)

    if size < 0:
        size = 0
    if size > data_count:
        size = data_count

    # derive the data splitter
    if shuffle:
        indices = np.arange(data_count)
        np.random.shuffle(indices)
        get_first = lambda v: v[indices[: -size]]
        get_second = lambda v: v[indices[-size:]]
    else:
        get_first = lambda v: v[: -size, ...]
        get_second = lambda v: v[-size:, ...]

    return (
        tuple(get_first(v) for v in arrays),
        tuple(get_second(v) for v in arrays)
    )
