# -*- coding: utf-8 -*-
import copy
import unittest

from mlcomp.report import ReportObject, default_report_types


class MyReportObject(ReportObject):

    def __init__(self, value=None, children=None, name=None, name_scope=None):
        super(MyReportObject, self).__init__(name=name, name_scope=name_scope)
        self.value = value
        if children:
            children = list(children)
        self.children = children

    def gather_children(self):
        if self.children:
            ret = copy.copy(self.children)
        else:
            ret = []
        ret.extend(super(MyReportObject, self).gather_children())
        return ret


class BaseTestCase(unittest.TestCase):

    MY_REPORT = (
        MyReportObject(
            value=MyReportObject(
                value=12345678,
                name='Child',
                children=[
                    MyReportObject(value=1),
                    MyReportObject(value=2),
                    MyReportObject(value=3, name='list_child'),
                    MyReportObject(value=4, name='list_child'),
                ]
            ),
            name='My Report'
        ),
        '{"__id__": 0, "__type__": "MyReport", "name": "My Report", "value": {"__id__": 1, "__type__": "MyReport", "children": [{"__id__": 2, "__type__": "MyReport", "value": 1}, {"__id__": 3, "__type__": "MyReport", "value": 2}, {"__id__": 4, "__type__": "MyReport", "name": "list_child", "value": 3}, {"__id__": 5, "__type__": "MyReport", "name": "list_child", "value": 4}], "name": "Child", "value": 12345678}}',
        "MyReportObject(name='My Report',value=MyReportObject(children=[MyReportObject(value=1), MyReportObject(value=2), MyReportObject(name='list_child',value=3), MyReportObject(name='list_child',value=4)],name='Child',value=12345678))"
    )

    def test_ReportObject(self):
        self.maxDiff = None
        with default_report_types({'MyReport': MyReportObject}):
            # test serialization and deserialization
            self.assertEqual(
                self.MY_REPORT[0].to_json(sort_keys=True),
                self.MY_REPORT[1]
            )
            self.assertEqual(
                repr(ReportObject.from_json(self.MY_REPORT[1])),
                self.MY_REPORT[2]
            )

            # test gather children
            self.assertEqual(
                self.MY_REPORT[0].gather_children(),
                [self.MY_REPORT[0].value]
            )
            self.assertEqual(
                self.MY_REPORT[0].value.gather_children(),
                self.MY_REPORT[0].value.children
            )

            # assign scope names
            obj = ReportObject.from_json(self.MY_REPORT[1])
            obj.assign_name_scopes()
            self.assertEqual(
                repr(obj), 
                "MyReportObject(name='My Report',name_scope='my_report',value=MyReportObject(children=[MyReportObject(name_scope='my_report/child/my_report_object',value=1), MyReportObject(name_scope='my_report/child/my_report_object_1',value=2), MyReportObject(name='list_child',name_scope='my_report/child/list_child',value=3), MyReportObject(name='list_child',name_scope='my_report/child/list_child_1',value=4)],name='Child',name_scope='my_report/child',value=12345678))"
            )

            # test multi-reference to a single report object
            obj.children = [obj.value.children[3]]
            obj.assign_name_scopes()
            self.assertEqual(
                repr(obj),
                "MyReportObject(children=[MyReportObject(name='list_child',name_scope='my_report/list_child',value=4)],name='My Report',name_scope='my_report',value=MyReportObject(children=[MyReportObject(name_scope='my_report/child/my_report_object',value=1), MyReportObject(name_scope='my_report/child/my_report_object_1',value=2), MyReportObject(name='list_child',name_scope='my_report/child/list_child',value=3), MyReportObject(name='list_child',name_scope='my_report/list_child',value=4)],name='Child',name_scope='my_report/child',value=12345678))"
            )


if __name__ == '__main__':
    unittest.main()
