# -*- coding: utf-8 -*-
__all__ = [
    'minibatch_slices_iterator', 'minibatch_iterator',
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
