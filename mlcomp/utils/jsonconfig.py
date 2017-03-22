# -*- coding: utf-8 -*-
from datetime import datetime
from json import JSONEncoder

import numpy as np
import pandas as pd
import six

__all__ = ['JsonConfigSerializer', 'JsonConfigObject']


class JsonConfigSerializer(JSONEncoder):
    """Extensible serializer class for `JsonConfigObject`.

    This class, as well as its derived classes, should define a set of rules
    to convert objects to JSON serializable values, and to convert these values
    back into desired types of objects.

    The basic serializer class defines these rules:

    *   Numpy arrays        <-> plain lists.
    *   Pandas data frames  <-> dict (as default orient).
    *   datetime            <-> timestamp numbers (of seconds).
    """

    def to_json_value(self, o):
        """Convert the object `o` to JSON serializable value.

        If `o` does not match any defined rule, it will be returned as-is.
        """
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, pd.DataFrame):
            return o.to_dict()
        if isinstance(o, datetime):
            return o.timestamp()
        return o

    def from_json_value(self, v, o_type):
        """Convert the JSON value `v` back to object according to `o_type`.

        If `o_type` does not match any defined rule, the value `v` will be
        returned as-is.
        """
        if issubclass(o_type, np.ndarray):
            return np.asarray(v)
        if issubclass(o_type, pd.DataFrame):
            return pd.DataFrame.from_dict(v)
        if issubclass(o_type, datetime):
            return datetime.fromtimestamp(v)
        return v


class JsonConfigObject(object):
    """JSON configurable object.

    This class provides a checked framework for serialization via JSON.
    Classes derived from `JsonConfigObject` or any descendant can specify
    the JSON serializable attributes via `__json_attributes__`.

    The `__json_attributes__` of all the ascendant classes will be collected
    to build up the rules for object serialization.
    Every entry of `__json_attributes__` should be a string mapped to a type
    (which defines the type of the attribute with that name), or None
    (which cancels out the attribute defined in ascendant classes).

    The serialization is done by calling `to_config` method of an instance.
    When it comes to deserialization, `from_config` method should be called
    to construct an instance from a JSON dict.  The `from_config` class method
    thus will construct objects from JSON values according to serialization
    rules, and call the constructor with those constructed objects, thus all
    the serializable attributes must be accepted by the constructor.
    """

    __json_serializer__ = JsonConfigSerializer
    __json_attributes__ = {}

    @classmethod
    def get_json_attributes(cls):
        """Get the JSON serializable attributes of this class."""
        ret = {}
        for b in reversed(cls.__bases__):
            if issubclass(b, JsonConfigObject):
                for k, v in six.iteritems(b.__json_attributes__):
                    if v is None:
                        ret.pop(k, None)
                    else:
                        ret[k] = v
        for k, v in six.iteritems(cls.__json_attributes__):
            if v is None:
                ret.pop(k, None)
            else:
                ret[k] = v
        return ret

    @classmethod
    def get_json_serializer(cls):
        """Get the JSON serializer of this class."""
        return cls.__json_serializer__()

    def to_config(self):
        """Get the JSON serializable dict of this object."""
        serializer = self.get_json_serializer()
        return {
            k: serializer.to_json_value(getattr(self, k, None))
            for k, _ in six.iteritems(self.get_json_attributes())
        }

    @classmethod
    def get_constructor_kwargs_from_config(cls, config_dict):
        """Get the constructor kwargs dict from the `config_dict`.

        If a defined attribute does not exist in `config_dict`, it will
        also be excluded from the returned kwargs dict.
        On the other hand, if an attribute is None in `config_dict`,
        it will keep None in the returned dict.

        Parameters
        ----------
        config_dict : dict[str, any]
            JSON serialized values.

        Returns
        -------
        dict[str, any]
            The kwargs which would be passed to constructor later.
        """
        serializer = cls.get_json_serializer()
        kwargs = {}
        for k, o_type in six.iteritems(cls.get_json_attributes()):
            if k in config_dict:
                v = config_dict[k]
                if v is None:
                    kwargs[k] = None
                else:
                    kwargs[k] = serializer.from_json_value(v, o_type)
        return kwargs

    @classmethod
    def from_config(cls, config_dict):
        """Construct an instance from the `config_dict`."""
        return cls(**cls.get_constructor_kwargs_from_config(config_dict))
