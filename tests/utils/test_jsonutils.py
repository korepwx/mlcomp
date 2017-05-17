# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import numpy as np

from mlcomp.utils import JsonEncoder, JsonDecoder, JsonBinary
from tests.helper import TestCase


class _MyObject(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'MyObject(%r)' % (self.value,)


class _MyJsonEncoder(JsonEncoder):

    def _my_object_handler(self, o):
        if isinstance(o, _MyObject):
            yield {'__type__': 'MyObject', 'value': o.value}
        elif isinstance(o, datetime):
            # test overriding the default datetime handler
            yield {'__type__': 'datetime', 'value': o.timetuple()[:6]}

    OBJECT_HANDLERS = [_my_object_handler] + JsonEncoder.OBJECT_HANDLERS


class _MyJsonDecoder(JsonDecoder):

    def _my_object_handler(self, v):
        if v['__type__'] == 'MyObject':
            yield _MyObject(v['value'])
        elif v['__type__'] == 'datetime':
            # test overriding the default datetime handler
            yield datetime(*tuple(v['value']))

    OBJECT_HANDLERS = [_my_object_handler] + JsonDecoder.OBJECT_HANDLERS


def assert_equal(x, y):
    if isinstance(x, list):
        if not isinstance(y, list) or len(x) != len(y):
            return False
        return all(assert_equal(xx, yy) for xx, yy in zip(x, y))
    elif isinstance(x, dict):
        if not isinstance(y, dict) or len(x) != len(y):
            return False
        keys = sorted(list(x.keys()))
        if keys != sorted(list(y.keys())):
            return False
        return all(assert_equal(x[k], y[k]) for k in keys)
    elif isinstance(x, np.ndarray):
        if not isinstance(y, np.ndarray) or x.shape != y.shape:
            return False
        return np.all(x == y)
    elif isinstance(x, _MyObject):
        if not isinstance(y, _MyObject):
            return False
        assert_equal(x.value, y.value)
    else:
        return x == y


BASIC_OBJECT = (
    {'a': 1,
     'b': np.asarray([0.5], dtype=np.float32)[0],
     'c': np.arange(16, dtype=np.int32),
     'd': [np.asarray(1, dtype=np.int64)],
     'e': {'__type__': 'nothing'}},
    '{"a": 1, "b": 0.5, "c": {"__id__": 0, "__type__": "ndarray", "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "dtype": "int32"}, "d": [{"__id__": 1, "__type__": "ndarray", "data": 1, "dtype": "int64"}], "e": {"__type__": "nothing"}}'
)
MY_OBJECT = (
    [_MyObject(1), _MyObject('2'), _MyObject(np.asarray(3, dtype=np.float32)),
     datetime(2000, 1, 1, 12, 0, 0)],
    '[{"__id__": 0, "__type__": "MyObject", "value": 1}, {"__id__": 1, "__type__": "MyObject", "value": "2"}, {"__id__": 2, "__type__": "MyObject", "value": {"__id__": 3, "__type__": "ndarray", "data": 3.0, "dtype": "float32"}}, {"__type__": "datetime", "value": [2000, 1, 1, 12, 0, 0]}]'
)
BINARY_OBJECT = (
    JsonBinary(b'abc'),
    '{"__id__": 0, "__type__": "binary", "data": "YWJj"}'
)
REF_OBJECT = (
    [BINARY_OBJECT[0], BINARY_OBJECT[0], _MyObject(BINARY_OBJECT[0])],
    '[{"__id__": 0, "__type__": "binary", "data": "YWJj"}, {"__id__": 0, "__type__": "ObjectRef"}, {"__id__": 1, "__type__": "MyObject", "value": {"__id__": 0, "__type__": "ObjectRef"}}]',
    '[{"__type__": "binary", "data": "YWJj"}, {"__type__": "binary", "data": "YWJj"}, {"__type__": "MyObject", "value": {"__type__": "binary", "data": "YWJj"}}]'
)


class JsonBinaryTestCase(TestCase):

    def test_errors(self):
        for obj in [1, True, None, u'']:
            with self.assertRaisesRegex(
                    TypeError, '`value` is not a binary object.'):
                JsonBinary(obj)

    def test_relation(self):
        self.assertTrue(JsonBinary(b'123') == JsonBinary(b'123'))
        self.assertTrue(JsonBinary(b'123') != JsonBinary(b'1234'))
        self.assertTrue(JsonBinary(b'123') < JsonBinary(b'1234'))
        self.assertTrue(JsonBinary(b'123') <= JsonBinary(b'1234'))
        self.assertTrue(JsonBinary(b'123') <= JsonBinary(b'123'))
        self.assertTrue(JsonBinary(b'1234') > JsonBinary(b'123'))
        self.assertTrue(JsonBinary(b'1234') >= JsonBinary(b'123'))
        self.assertTrue(JsonBinary(b'123') >= JsonBinary(b'123'))

    def test_hash(self):
        self.assertEqual(
            hash(JsonBinary(b'123')), hash(JsonBinary(b'123')))


class JsonEncoderTestCase(TestCase):

    def test_basic_encoder(self):
        e = JsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(BASIC_OBJECT[0]), BASIC_OBJECT[1])

    def test_customized_encoder(self):
        e = _MyJsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(MY_OBJECT[0]), MY_OBJECT[1])

    def test_binary_object(self):
        e = JsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(BINARY_OBJECT[0]), BINARY_OBJECT[1])

    def test_object_ref_enabled(self):
        e = _MyJsonEncoder(sort_keys=True)
        self.assertEqual(e.encode(REF_OBJECT[0]), REF_OBJECT[1])

    def test_object_ref_disabled(self):
        e = _MyJsonEncoder(sort_keys=True, object_ref=False)
        self.assertEqual(e.encode(REF_OBJECT[0]), REF_OBJECT[2])


class JsonDecoderTestCase(TestCase):

    def test_basic_decoder(self):
        d = JsonDecoder()
        assert_equal(d.decode(BASIC_OBJECT[1]), BASIC_OBJECT[0])

    def test_customized_decoder(self):
        d = _MyJsonDecoder()
        assert_equal(d.decode(MY_OBJECT[1]), MY_OBJECT[0])

    def test_binary_object(self):
        d = JsonDecoder()
        self.assertEqual(d.decode(BINARY_OBJECT[1]), BINARY_OBJECT[0])

    def test_object_ref_enabled(self):
        d = _MyJsonDecoder()
        decoded = d.decode(REF_OBJECT[1])
        assert_equal(decoded, REF_OBJECT[0])
        self.assertIs(decoded[1], decoded[0])
        self.assertIs(decoded[2].value, decoded[0])

    def test_object_ref_error(self):
        with self.assertRaisesRegex(
                KeyError, r'Object reference .* is not defined.'):
            JsonDecoder().decode('{"__id__": 0, "__type__": "ObjectRef"}')

    def test_extra_object_hook(self):
        def my_hook(o):
            if o.get('__type__', None) == 'abc':
                return o['value']
            return o

        d = JsonDecoder(object_hook=my_hook)
        self.assertEqual(
            d.decode('{"a": 1, "b": {"__type__": "abc", "value": 2}, "c": {"__id__": 0, "__type__": "binary", "data": "YWJj"}}'),
            {'a': 1, 'b': 2, 'c': JsonBinary(b'abc')}
        )


if __name__ == '__main__':
    unittest.main()
