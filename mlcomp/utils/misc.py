# -*- coding: utf-8 -*-
import re
import sys
import threading
from collections import OrderedDict
from datetime import datetime, date
from itertools import chain

import six

__all__ = [
    'unique', 'sorted_unique', 'AutoReprObject', 'object_to_dict',
    'camel_to_underscore', 'import_string', 'ContextStack',
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


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).
    If `silent` is True the return value will be `None` if the import fails.

    Source: werkzeug.utils.import_string

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError:
        if not silent:
            raise


class ContextStack(object):
    """Thread-local context stack for general purpose.
    
    Parameters
    ----------
    initial_factory : () -> any
        If specified, fill the context stack with an initial object
        generated by this factory.
    """

    _STORAGE_STACK_KEY = '_context_stack'

    def __init__(self, initial_factory=None):
        self._storage = threading.local()
        self._initial_factory = initial_factory

    @property
    def items(self):
        if not hasattr(self._storage, self._STORAGE_STACK_KEY):
            new_stack = []
            if self._initial_factory is not None:
                new_stack.append(self._initial_factory())
            setattr(self._storage, self._STORAGE_STACK_KEY, new_stack)
        return getattr(self._storage, self._STORAGE_STACK_KEY)

    def push(self, context):
        self.items.append(context)

    def pop(self):
        self.items.pop()

    def top(self):
        items = self.items
        if items:
            return items[-1]
