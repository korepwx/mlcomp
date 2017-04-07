# -*- coding: utf-8 -*-
import unittest

from mlcomp.report import Container, ReportObject, default_report_types


class MyReport(ReportObject):
    def __init__(self, value):
        super(MyReport, self).__init__()
        self.value = value


class MyTestCase(unittest.TestCase):

    def test_ChildrenFlatten(self):
        # test children flatten
        c = Container([
            MyReport(1),
            [
                MyReport(2),
                MyReport(3)
            ],
            (
                MyReport(4),
                [
                    MyReport(5),
                    MyReport(6),
                ]
            )
        ])
        c.add(
            MyReport(7),
            [
                MyReport(8),
                (
                    MyReport(9),
                    MyReport(0),
                )
            ]
        )
        with default_report_types({'MyReport': MyReport}):
            self.maxDiff = None
            self.assertEqual(
                c.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "Container", "children": [{"__id__": 1, "__type__": "MyReport", "value": 1}, [{"__id__": 2, "__type__": "MyReport", "value": 2}, {"__id__": 3, "__type__": "MyReport", "value": 3}], [{"__id__": 4, "__type__": "MyReport", "value": 4}, [{"__id__": 5, "__type__": "MyReport", "value": 5}, {"__id__": 6, "__type__": "MyReport", "value": 6}]], {"__id__": 7, "__type__": "MyReport", "value": 7}, [{"__id__": 8, "__type__": "MyReport", "value": 8}, [{"__id__": 9, "__type__": "MyReport", "value": 9}, {"__id__": 10, "__type__": "MyReport", "value": 0}]]]}'
            )


if __name__ == '__main__':
    unittest.main()
