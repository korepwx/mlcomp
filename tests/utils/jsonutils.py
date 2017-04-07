# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import numpy as np
import six

from mlcomp.utils import JsonEncoder, JsonDecoder, JsonBinary


class MyObject(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'MyObject(%r)' % (self.value,)


class MyJsonEncoder(JsonEncoder):

    def _my_object_handler(self, o):
        if isinstance(o, MyObject):
            yield {'__type__': 'MyObject', 'value': o.value}
        if isinstance(o, datetime):
            # test overriding the default datetime handler
            yield {'__type__': 'datetime', 'value': o.timestamp()}

    OBJECT_HANDLERS = [_my_object_handler] + JsonEncoder.OBJECT_HANDLERS


class MyJsonDecoder(JsonDecoder):

    def _my_object_handler(self, v):
        if v['__type__'] == 'MyObject':
            yield MyObject(v['value'])
        elif v['__type__'] == 'datetime':
            # test overriding the default datetime handler
            yield datetime.fromtimestamp(v['value'])

    OBJECT_HANDLERS = [_my_object_handler] + JsonDecoder.OBJECT_HANDLERS


class JsonUtilsTestCase(unittest.TestCase):

    BASIC_OBJECT = (
        {'a': 1, 'b': datetime(2000, 1, 1), 'c': np.arange(16, dtype=np.int32),
         'd': [np.asarray(1)], 'e': {'__type__': 'nothing'}},
        '{"a": 1, "b": {"__type__": "datetime", "value": 946656000000.0}, "c": {"__id__": 0, "__type__": "ndarray", "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "dtype": "int32"}, "d": [{"__id__": 1, "__type__": "ndarray", "data": 1, "dtype": "int64"}], "e": {"__type__": "nothing"}}'
    )
    MY_OBJECT = (
        [MyObject(1), MyObject('2'), MyObject(np.asarray(3, dtype=np.float32)),
         datetime(2000, 1, 1)],
        '[{"__id__": 0, "__type__": "MyObject", "value": 1}, {"__id__": 1, "__type__": "MyObject", "value": "2"}, {"__id__": 2, "__type__": "MyObject", "value": {"__id__": 3, "__type__": "ndarray", "data": 3.0, "dtype": "float32"}}, {"__type__": "datetime", "value": 946656000.0}]'
    )
    BINARY_OBJECT = (
        JsonBinary(b'abc'),
        '{"__id__": 0, "__type__": "binary", "data": "YWJj"}'
    )
    PLAIN_BINARY_OBJECT = (
        b'abc',
        '{"__id__": 0, "__type__": "binary", "data": "YWJj"}'
    )
    REF_OBJECT = (
        [BINARY_OBJECT[0], BINARY_OBJECT[0], MyObject(BINARY_OBJECT[0])],
        '[{"__id__": 0, "__type__": "binary", "data": "YWJj"}, {"__id__": 0, "__type__": "ObjectRef"}, {"__id__": 1, "__type__": "MyObject", "value": {"__id__": 0, "__type__": "ObjectRef"}}]',
        '[{"__type__": "binary", "data": "YWJj"}, {"__type__": "binary", "data": "YWJj"}, {"__type__": "MyObject", "value": {"__type__": "binary", "data": "YWJj"}}]'
    )

    def test_JsonEncoder(self):
        # test basic json encoder
        e = ReportJsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(self.BASIC_OBJECT[0]), self.BASIC_OBJECT[1])

        # test customized json encoder
        e = MyJsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(self.MY_OBJECT[0]), self.MY_OBJECT[1])

    def test_JsonDecoder(self):
        # test basic json decoder
        d = ReportJsonDecoder()
        self.assertEqual(repr(d.decode(self.BASIC_OBJECT[1])),
                         repr(self.BASIC_OBJECT[0]))

        # test customized json decoder
        d = MyJsonDecoder()
        self.assertEqual(repr(d.decode(self.MY_OBJECT[1])),
                         repr(self.MY_OBJECT[0]))

    def test_BinaryObject(self):
        e = ReportJsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(self.BINARY_OBJECT[0]), self.BINARY_OBJECT[1])
        if six.PY3:
            self.assertEqual(e.encode(self.PLAIN_BINARY_OBJECT[0]),
                             self.PLAIN_BINARY_OBJECT[1])

        d = ReportJsonDecoder()
        self.assertEqual(d.decode(self.BINARY_OBJECT[1]), self.BINARY_OBJECT[0])
        if six.PY3:
            self.assertEqual(d.decode(self.PLAIN_BINARY_OBJECT[1]),
                             self.PLAIN_BINARY_OBJECT[0])

    def test_ObjectRef(self):
        # test object_ref = True
        e = MyJsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(self.REF_OBJECT[0]), self.REF_OBJECT[1])

        d = MyJsonDecoder()
        decoded = d.decode(self.REF_OBJECT[1])
        self.assertEqual(repr(decoded), repr(self.REF_OBJECT[0]))
        self.assertIs(decoded[1], decoded[0])
        self.assertIs(decoded[2].value, decoded[0])

        # test object_ref = False
        e = MyJsonEncoder(sort_keys=True, object_ref=False)
        self.assertEqual(e.encode(self.REF_OBJECT[0]), self.REF_OBJECT[2])

if __name__ == '__main__':
    unittest.main()
