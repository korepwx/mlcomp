# -*- coding: utf-8 -*-

import unittest

from qualname import qualname

from mlcomp.report import Report
from tests.report.helpers import MyReport


class BaseTestCase(unittest.TestCase):

    def test_Serialization(self):
        r = Report('Hello World', children=[
            MyReport(
                1234, 'Hi, Google', children=[Report('abc')]),
            Report('Hey, Apple')
        ])
        self.assertEquals(
            repr(r),
            "Report(children=[MyReport(c=1234,children=["
            "Report(title='abc')],title='Hi, Google'), Report(title='Hey, "
            "Apple')],title='Hello World')"
        )

        # test to_config and from_config in safe-mode
        self.assertEquals(
            r.to_config({MyReport: 'MyReport'}),
            {'children': [{'c': 1234,
                           'children': [{'title': 'abc', 'type': 'Report'}],
                           'title': 'Hi, Google',
                           'type': 'MyReport'},
                          {'title': 'Hey, Apple', 'type': 'Report'}],
             'title': 'Hello World',
             'type': 'Report'}
        )
        r2 = Report.from_config(
            r.to_config({MyReport: 'MyReport'}),
            report_types={'MyReport': MyReport}
        )
        self.assertEquals(repr(r2), repr(r))

        # test to_config and from_config in non safe-mode
        type_name = MyReport.__module__ + '.' + qualname(MyReport)
        self.assertNotEquals(type_name, 'MyReport')
        self.assertEquals(
            r.to_config(),
            {'children': [{'c': 1234,
                           'children': [{'title': 'abc', 'type': 'Report'}],
                           'title': 'Hi, Google',
                           'type': type_name},
                          {'title': 'Hey, Apple', 'type': 'Report'}],
             'title': 'Hello World',
             'type': 'Report'}
        )
        r2 = Report.from_config(r.to_config(), safe_mode=False)
        self.assertEquals(repr(r2), repr(r))

        # test importing a qualified name in safe-mode
        with self.assertRaises(KeyError):
            Report.from_config(r.to_config())
