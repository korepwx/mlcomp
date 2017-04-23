# -*- coding: utf-8 -*-
import unittest

from mlcomp.report import (ReportTypes, ReportObject, HTML,
                           get_default_report_types, default_report_types)


class MyReport(ReportObject):
    pass

my_report_name = MyReport.__module__ + '.MyReport'


class TypesTestCase(unittest.TestCase):

    def test_name_to_type(self):
        ctx = ReportTypes()
        self.assertIs(ctx.name_to_type('ReportObject'), ReportObject)
        self.assertIs(ctx.name_to_type('HTML'), HTML)
        with self.assertRaises(TypeError):
            ctx.name_to_type('ReportTypes')
        with self.assertRaises(KeyError):
            ctx.name_to_type('MyReport')
        with self.assertRaises(KeyError):
            ctx.name_to_type(my_report_name)

        ctx = ReportTypes({'MyReport': MyReport})
        self.assertIs(ctx.name_to_type('ReportObject'), ReportObject)
        self.assertIs(ctx.name_to_type('HTML'), HTML)
        with self.assertRaises(TypeError):
            ctx.name_to_type('ReportTypes')
        self.assertIs(ctx.name_to_type('MyReport'), MyReport)
        with self.assertRaises(KeyError):
            ctx.name_to_type(my_report_name)

        ctx = ReportTypes({'HTML': MyReport}, safe_mode=False)
        self.assertIs(ctx.name_to_type('ReportObject'), ReportObject)
        self.assertIs(ctx.name_to_type('HTML'), MyReport)
        with self.assertRaises(TypeError):
            ctx.name_to_type('ReportTypes')
        with self.assertRaises(TypeError):
            ctx.name_to_type(TypesTestCase.__module__ + '.TypesTestCase')
        with self.assertRaises(KeyError):
            ctx.name_to_type('MyReport')
        self.assertIs(ctx.name_to_type(my_report_name), MyReport)

    def test_type_to_name(self):
        ctx = ReportTypes()
        self.assertEqual(ctx.type_to_name(ReportObject), 'ReportObject')
        self.assertEqual(ctx.type_to_name(HTML), 'HTML')
        with self.assertRaises(TypeError):
            ctx.type_to_name(ReportTypes)
        with self.assertRaises(KeyError):
            ctx.type_to_name(MyReport)

        ctx = ReportTypes({'MyReport': MyReport})
        self.assertEqual(ctx.type_to_name(ReportObject), 'ReportObject')
        self.assertEqual(ctx.type_to_name(HTML), 'HTML')
        with self.assertRaises(TypeError):
            ctx.type_to_name(ReportTypes)
        self.assertEqual(ctx.type_to_name(MyReport), 'MyReport')

        ctx = ReportTypes({'HTML': MyReport}, safe_mode=False)
        self.assertEqual(ctx.type_to_name(ReportObject), 'ReportObject')
        self.assertEqual(ctx.type_to_name(MyReport), 'HTML')

        ctx = ReportTypes(safe_mode=False)
        self.assertEqual(ctx.type_to_name(ReportObject), 'ReportObject')
        self.assertEqual(ctx.type_to_name(HTML), 'HTML')
        self.assertEqual(ctx.type_to_name(MyReport), my_report_name)

    def test_context(self):
        ctx = get_default_report_types()
        self.assertTrue(ctx.safe_mode)
        self.assertEqual(ctx.mappings, {})

        with default_report_types({'MyReport': MyReport}, safe_mode=False):
            ctx = get_default_report_types()
            self.assertFalse(ctx.safe_mode)
            self.assertEqual(ctx.mappings, {'MyReport': MyReport})

            with default_report_types({'HTML': MyReport}):
                ctx = get_default_report_types()
                self.assertFalse(ctx.safe_mode)
                self.assertEqual(
                    ctx.mappings, {'MyReport': MyReport, 'HTML': MyReport})

            ctx = get_default_report_types()
            self.assertFalse(ctx.safe_mode)
            self.assertEqual(ctx.mappings, {'MyReport': MyReport})

        ctx = get_default_report_types()
        self.assertTrue(ctx.safe_mode)
        self.assertEqual(ctx.mappings, {})

if __name__ == '__main__':
    unittest.main()
