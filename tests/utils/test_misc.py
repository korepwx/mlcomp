# -*- coding: utf-8 -*-
import unittest

from mlcomp.utils import camel_to_underscore


class MiscTestCase(unittest.TestCase):

    def test_camel_to_underscore(self):
        def assert_convert(camel, underscore):
            self.assertEqual(
                camel_to_underscore(camel),
                underscore,
                msg='%r should be converted to %r.' % (camel, underscore)
            )

        examples = [
            ('simpleTest', 'simple_test'),
            ('easy', 'easy'),
            ('HTML', 'html'),
            ('simpleXML', 'simple_xml'),
            ('PDFLoad', 'pdf_load'),
            ('startMIDDLELast', 'start_middle_last'),
            ('AString', 'a_string'),
            ('Some4Numbers234', 'some4_numbers234'),
            ('TEST123String', 'test123_string'),
        ]
        for camel, underscore in examples:
            assert_convert(camel, underscore)
            assert_convert(underscore, underscore)
            assert_convert('_%s_' % camel, '_%s_' % underscore)
            assert_convert('_%s_' % underscore, '_%s_' % underscore)
            assert_convert('__%s__' % camel, '__%s__' % underscore)
            assert_convert('__%s__' % underscore, '__%s__' % underscore)
            assert_convert(
                '_'.join([s.capitalize() for s in underscore.split('_')]),
                underscore
            )
            assert_convert(
                '_'.join([s.upper() for s in underscore.split('_')]),
                underscore
            )

if __name__ == '__main__':
    unittest.main()
