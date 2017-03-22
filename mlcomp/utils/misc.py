# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from datetime import datetime, date
from itertools import chain

import six

__all__ = [
    'unique', 'sorted_unique', 'AutoReprObject', 'object_to_dict',
    'camel_to_underscore',
]

NON_OBJECT_TYPES = (
    six.string_types + six.integer_types +
    (float, bool, tuple, list, datetime, date)
)


def unique(iterable):
    """Uniquify elements to construct a new list.

    Parameters
    ----------
    iterable : collections.Iterable[any]
        The collection to be uniquified.

    Returns
    -------
    list[any]
        Unique elements as a list, whose orders are preserved.
    """
    def small():
        ret = []
        for e in iterable:
            if e not in ret:
                ret.append(e)
        return ret

    def large():
        ret = []
        memo = set()
        for e in iterable:
            if e not in memo:
                memo.add(e)
                ret.append(e)
        return ret

    if hasattr(iterable, '__len__'):
        if len(iterable) < 1000:
            return small()
    return large()


def sorted_unique(iterable):
    """Sort and uniquify elements to construct a new list.

    Parameters
    ----------
    iterable : collections.Iterable[any]
        The collection to be sorted and uniquified.

    Returns
    -------
    list[any]
        Unique elements as a sorted list.
    """
    return sorted(set(iterable))


class AutoReprObject(object):
    """Base class for objects with automatic repr implementation.

    The automatic repr implementation will demonstrate all the attributes
    in repr function.  To control the order of these attributes, one may
    provide an attribute list in `__repr_attributes__` class variable.
    """

    __repr_attributes__ = None
    __repr_value_length__ = None

    def __repr__(self):
        def truncate(s):
            maxlen = self.__repr_value_length__
            if maxlen is None or len(s) < maxlen:
                return s
            return '%s...' % (s[: maxlen],)

        repr_attrs = getattr(self, '__repr_attributes__') or ()
        repr_attrs = unique(chain(repr_attrs, sorted(self.__dict__)))
        pieces = ','.join(
            '%s=%s' % (k, truncate(repr(v)))
            for k, v in ((k, getattr(self, k)) for k in repr_attrs) if v
        )
        return '%s(%s)' % (self.__class__.__name__, pieces)


def object_to_dict(o, ordered_dict=True, recursive=True):
    """Convert the object to dict.

    The attributes accessible from o.__dict__ will be extracted and
    converted to a dict.

    Parameters
    ----------
    o : any
        The object to be converted into dict.

        If the object is a plain object rather than an object,
        will return the object itself directly.

    ordered_dict : bool
        Use an ordered dict to store the attributes (in alphabetic order).

        If the object is inherited from AutoReprObject, the attribute
        will follow the order specified by `__repr_attributes__`.

    recursive : bool
        Whether or not to recursively convert object into dict.

    Returns
    -------
    dict | any
    """
    if o is None or isinstance(o, NON_OBJECT_TYPES):
        return o
    attrs = getattr(o, '__repr_attributes__', None) or ()
    attrs = unique(chain(attrs, sorted(o.__dict__)))
    dict_type = OrderedDict if ordered_dict else dict
    convert_obj = object_to_dict if recursive else (lambda v: v)
    return dict_type((k, convert_obj(getattr(o, k))) for k in attrs)


def camel_to_underscore(name):
    """Convert a camel-case name to underscore."""
    s1 = re.sub(CAMEL_TO_UNDERSCORE_S1, r'\1_\2', name)
    return re.sub(CAMEL_TO_UNDERSCORE_S2, r'\1_\2', s1).lower()

CAMEL_TO_UNDERSCORE_S1 = re.compile('(.)([A-Z][a-z]+)')
CAMEL_TO_UNDERSCORE_S2 = re.compile('([a-z0-9])([A-Z])')
