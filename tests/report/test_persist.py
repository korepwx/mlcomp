# -*- coding: utf-8 -*-
import copy
import os
import unittest

from mlcomp.utils import TemporaryDirectory
from mlcomp.report import (ReportSaver, ReportObject, Resource,
                           default_report_types)


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


class PersistTestCase(unittest.TestCase):

    def test_ReportSaver(self):
        report = MyReportObject(
            value=123456789,
            children=[
                Resource(data=b'123'),
                MyReportObject(
                    Resource(data=b'456'),
                    children=[
                        Resource(data=b'789')
                    ]
                )
            ]
        )

        with default_report_types({'MyReport': MyReportObject}), \
                TemporaryDirectory() as tempdir:
            # test writing
            saver = ReportSaver(tempdir + '/1')
            saver.save(report)
            report2 = saver.load()
            self.assertEqual(repr(report), repr(report2))
            self.assertEqual(report.children[0].data,
                             report2.children[0].data)
            self.assertEqual(report.children[1].value.data,
                             report2.children[1].value.data)
            self.assertEqual(report.children[1].children[0].data,
                             report2.children[1].children[0].data)

            # writing to exist dir will be refused
            with self.assertRaises(IOError):
                saver.save(report)

            # test writing to exist but empty dir
            os.makedirs(tempdir + '/2')
            saver = ReportSaver(tempdir + '/2')
            saver.save(report)

            # test force writing
            saver = ReportSaver(tempdir + '/2', overwrite=True)
            saver.save(report)


if __name__ == '__main__':
    unittest.main()

