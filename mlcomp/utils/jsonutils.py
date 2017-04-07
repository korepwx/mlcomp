# -*- coding: utf-8 -*-
import json
from base64 import b64encode, b64decode
from datetime import datetime

import numpy as np
import six

__all__ = [
    'JsonBinary', 'JsonEncoder', 'JsonDecoder',
]


class JsonBinary(six.binary_type):
    """Wrapper class for binary objects.
    
    In Python2, ordinary strings are binary strings, thus we cannot encode
    the binary strings into base64 strings directly.  In this case, one
    may explicitly wrap such a binary string in this class to inform the
    encoder.
    """


class JsonEncoder(json.JSONEncoder):
    """Extended JSON encoder with support of the following types:

    *   bytes | JsonBinary ->
            {'__type__': 'binary', 'data': base64 encoded}
    *   numpy.integer ->
            int
    *   numpy.ndarray -> 
            {'__type__': 'ndarray', 'data': o.tolist(), 'dtype': o.dtype}
    *   datetime.datetime ->
            {'__type__': 'datetime', 'value': o.timestamp() * 1000}
            
    Besides, if the same (customized) object is referenced for multiple
    times, and if `object_ref` is set to True, it will only be serialized
    only at its first occurrence.  All later occurrences will be saved as:
    
        {'__type__': 'ObjectRef', 'id': ...}.
        
    Parameters
    ----------
    object_ref : bool
        Whether or not to allow serializing same object as references?
        (default True)
    """

    BINARY_TYPES = (six.binary_type, JsonBinary) if six.PY3 else JsonBinary
    NO_REF_TYPES = six.integer_types + (float, bool, datetime,)

    def __init__(self, object_ref=True, **kwargs):
        super(JsonEncoder, self).__init__(**kwargs)
        self.object_ref = object_ref
        self._ref_dict = {}

    def _default_object_handler(self, o):
        if isinstance(o, self.BINARY_TYPES):
            cnt = b64encode(o).decode('utf-8')
            yield {'__type__': 'binary', 'data': cnt}
        elif isinstance(o, np.integer):
            yield int(o)
        elif isinstance(o, np.ndarray):
            yield {
                '__type__': 'ndarray',
                'data': o.tolist(),
                'dtype': str(o.dtype)
            }
        elif isinstance(o, datetime):
            yield {'__type__': 'datetime', 'value': o.timestamp() * 1000}

    #: List of object serialization handlers
    OBJECT_HANDLERS = [_default_object_handler]

    def clear_object_ref(self):
        """Clear all serialized object references."""
        self._ref_dict.clear()

    def default(self, o):
        o_id = id(o)
        if self.object_ref:
            if o_id in self._ref_dict:
                return {'__type__': 'ObjectRef', '__id__': self._ref_dict[o_id]}
        for handler in self.OBJECT_HANDLERS:
            for obj in handler(self, o):
                if self.object_ref and isinstance(obj, dict) and \
                        not isinstance(o, self.NO_REF_TYPES):
                    self._ref_dict[o_id] = len(self._ref_dict)
                    obj['__id__'] = self._ref_dict[o_id]
                return obj
        return super(JsonEncoder, self).default(o)

    def encode(self, o):
        self.clear_object_ref()
        return super(JsonEncoder, self).encode(o)


class JsonDecoder(json.JSONDecoder):
    """Extended JSON decoder coupled with `mlcomp.utils.JsonEncoder`."""

    def __init__(self, **kwargs):
        self._object_hook = kwargs.get('object_hook', None)
        self._ref_dict = {}
        kwargs['object_hook'] = self._injected_object_hook
        kwargs.setdefault('object_hook', self._injected_object_hook)
        super(JsonDecoder, self).__init__(**kwargs)

    def clear_object_ref(self):
        """Clear all deserialized object references."""
        self._ref_dict.clear()

    def _default_object_handler(self, v):
        v_type = v['__type__']
        if v_type == 'binary':
            yield JsonBinary(b64decode(v['data']))
        elif v_type == 'ndarray':
            yield np.asarray(v['data'], dtype=v['dtype'])
        elif v_type == 'datetime':
            yield datetime.fromtimestamp(v['value'] / 1000.0)

    #: List of object deserialization handlers
    OBJECT_HANDLERS = [_default_object_handler]

    def _injected_object_hook(self, v):
        v_type = v.get('__type__', None)
        if v_type == 'ObjectRef':
            v_id = v['__id__']
            if v_id not in self._ref_dict:
                raise KeyError('Object reference %r is not defined.' % (v_id,))
            return self._ref_dict[v_id]
        elif v_type is not None:
            for handler in self.OBJECT_HANDLERS:
                for o in handler(self, v):
                    v_id = v.get('__id__', None)
                    if v_id is not None:
                        self._ref_dict[v_id] = o
                    return o
        if self._object_hook is not None:
            v = self._object_hook(v)
        return v
