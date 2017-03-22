# -*- coding: utf-8 -*-

import unittest

from mlcomp.report import Report, register_report_type


class BaseTestCase(unittest.TestCase):

    def test_Serialization(self):
        class SerializationTestReport(Report):
            __json_attributes__ = {
                'c': int
            }

            def __init__(self, c, title, children=None):
                super(SerializationTestReport, self).__init__(title, children)
                self.c = c

        register_report_type(SerializationTestReport)
        r = Report('Hello World', children=[
            SerializationTestReport(
                1234, 'Hi, Google', children=[Report('abc')]),
            Report('Hey, Apple')
        ])
        self.assertEquals(
            repr(r),
            "Report(children=[SerializationTestReport(c=1234,children=["
            "Report(title='abc')],title='Hi, Google'), Report(title='Hey, "
            "Apple')],title='Hello World')"
        )
        self.assertEquals(
            r.to_config(),
            {'children': [{'c': 1234,
                           'children': [{'title': 'abc', 'type': 'Report'}],
                           'title': 'Hi, Google',
                           'type': 'SerializationTestReport'},
                          {'title': 'Hey, Apple', 'type': 'Report'}],
             'title': 'Hello World',
             'type': 'Report'}
        )
        r2 = Report.from_config(r.to_config())
        self.assertEquals(repr(r2), repr(r))
