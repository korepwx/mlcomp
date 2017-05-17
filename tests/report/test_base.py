# -*- coding: utf-8 -*-
import copy
import unittest

from mlcomp.report import ReportObject, default_report_types
from .helper import to_config


class _MyReportObject(ReportObject):

    def __init__(self, value=None, children=None, name=None, name_scope=None):
        super(_MyReportObject, self).__init__(name=name, name_scope=name_scope)
        self.value = value
        if children:
            children = list(children)
        self.children = children

    def gather_children(self):
        if self.children:
            ret = copy.copy(self.children)
        else:
            ret = []
        ret.extend(super(_MyReportObject, self).gather_children())
        return ret


class ReportObjectTestCase(unittest.TestCase):

    MY_REPORT = (
        _MyReportObject(
            value=_MyReportObject(
                value=12345678,
                name='Child',
                children=[
                    _MyReportObject(value=1),
                    _MyReportObject(value=2),
                    _MyReportObject(value=3, name='list_child'),
                    _MyReportObject(value=4, name='list_child'),
                ]
            ),
            name='My Report'
        ),
        '{"__id__": 0, "__type__": "MyReport", "name": "My Report", "value": {"__id__": 1, "__type__": "MyReport", "children": [{"__id__": 2, "__type__": "MyReport", "value": 1}, {"__id__": 3, "__type__": "MyReport", "value": 2}, {"__id__": 4, "__type__": "MyReport", "name": "list_child", "value": 3}, {"__id__": 5, "__type__": "MyReport", "name": "list_child", "value": 4}], "name": "Child", "value": 12345678}}',
    )

    def test_serialization(self):
        with default_report_types({'MyReport': _MyReportObject}):
            # test serialization and deserialization
            self.assertEqual(
                self.MY_REPORT[0].to_json(sort_keys=True),
                self.MY_REPORT[1]
            )
            self.assertEqual(
                to_config(ReportObject.from_json(self.MY_REPORT[1])),
                to_config(self.MY_REPORT[0])
            )

    def test_gather_children(self):
        with default_report_types({'MyReport': _MyReportObject}):
            self.assertEqual(
                self.MY_REPORT[0].gather_children(),
                [self.MY_REPORT[0].value]
            )
            self.assertEqual(
                self.MY_REPORT[0].value.gather_children(),
                self.MY_REPORT[0].value.children
            )

    def test_assign_name_scopes(self):
        with default_report_types({'MyReport': _MyReportObject}):
            obj = ReportObject.from_json(self.MY_REPORT[1])
            obj.assign_name_scopes()
            self.assertEqual(
                to_config(obj),
                {'name': 'My Report',
                 'name_scope': 'my_report',
                 'value': {'children': [{'name_scope': 'my_report/child/my_report_object',
                                         'value': 1},
                                        {'name_scope': 'my_report/child/my_report_object_1',
                                         'value': 2},
                                        {'name': 'list_child',
                                         'name_scope': 'my_report/child/list_child',
                                         'value': 3},
                                        {'name': 'list_child',
                                         'name_scope': 'my_report/child/list_child_1',
                                         'value': 4}],
                           'name': 'Child',
                           'name_scope': 'my_report/child',
                           'value': 12345678}}
            )

    def test_multi_references(self):
        with default_report_types({'MyReport': _MyReportObject}):
            obj = ReportObject.from_json(self.MY_REPORT[1])
            obj.children = [obj.value.children[3]]
            obj.assign_name_scopes()
            self.assertEqual(
                to_config(obj),
                {'children': [{'name': 'list_child',
                               'name_scope': 'my_report/list_child',
                               'value': 4}],
                 'name': 'My Report',
                 'name_scope': 'my_report',
                 'value': {'children': [{'name_scope': 'my_report/child/my_report_object',
                                         'value': 1},
                                        {'name_scope': 'my_report/child/my_report_object_1',
                                         'value': 2},
                                        {'name': 'list_child',
                                         'name_scope': 'my_report/child/list_child',
                                         'value': 3},
                                        {'name': 'list_child',
                                         'name_scope': 'my_report/list_child',
                                         'value': 4}],
                           'name': 'Child',
                           'name_scope': 'my_report/child',
                           'value': 12345678}}
            )


if __name__ == '__main__':
    unittest.main()
