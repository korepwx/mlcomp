# -*- coding: utf-8 -*-
import copy
import gzip
import os
import unittest

import six

from mlcomp.report import (Resource, ResourceManager, ReportObject,
                           default_report_types, Report)
from mlcomp.utils import TemporaryDirectory
from .helper import to_config


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


class ResourceTestCase(unittest.TestCase):

    def test_Resource(self):
        R = Resource

        # test construction
        with self.assertRaises(ValueError):
            R(data=None, path=None)

        # test indicators
        self.assertFalse(R(b'').has_saved)
        self.assertTrue(R(b'').has_loaded)
        self.assertTrue(R(path='1.jpg').has_saved)
        self.assertFalse(R(path='1.jpg').has_loaded)

        # test extension infer
        self.assertEqual(R(b'', extension='.bmp').extension, '.bmp')
        self.assertEqual(R(b'', path='1.jpg').extension, '.jpg')
        self.assertEqual(R(b'', content_type='image/png').extension, '.png')

        # test content-type infer
        self.assertEqual(R(b'', content_type='image/x-ms-bmp').content_type,
                         'image/x-ms-bmp')
        self.assertEqual(R(b'', path='1.jpg').content_type, 'image/jpeg')
        self.assertEqual(R(b'', extension='.png').content_type, 'image/png')

        # test to config
        self.assertEqual(
            R(b'123', path='4.jpg', extension='.png',
              content_type='image/x-ms-bmp', name='Pic',
              name_scope='pic').to_config(),
            {'content_type': 'image/x-ms-bmp',
             'extension': '.png',
             'name': 'Pic',
             'name_scope': 'pic',
             'path': '4.jpg'}
        )
        self.assertEqual(
            R(b'123', path='4.jpg').to_config(),
            {'path': '4.jpg'}
        )

    def test_ResourceManager(self):
        # test without `rel_path`
        with TemporaryDirectory() as tempdir:
            rm = ResourceManager(save_dir=tempdir, rel_path='')
            with self.assertRaises(ValueError):
                rm.save(b'', '', extension='')
            with self.assertRaises(TypeError):
                rm.save(six.text_type(''), 'x', extension='')

            # /1.txt
            with self.assertRaises(IOError):
                rm.load('1.txt')
            self.assertEqual(rm.save(b'123', '1', extension='.txt'),
                             '1.txt')
            self.assertEqual(rm.load('1.txt'), b'123')

            # /2
            self.assertEqual(rm.save(b'456', '2', extension=''), '2')
            self.assertEqual(rm.load('2'), b'456')

            # /3/4/5.txt
            self.assertEqual(rm.save(b'789', '3/4/5', extension='.txt'),
                             '3/4/5.txt')
            self.assertEqual(rm.load('3/4/5.txt'), b'789')

        # test with `rel_path`
        with TemporaryDirectory() as tempdir:
            rm = ResourceManager(save_dir=tempdir, rel_path='res')

            # /3/4/5.txt
            self.assertEqual(rm.save(b'789', '3/4/5', extension='.txt'),
                             'res/3/4/5.txt')
            self.assertEqual(rm.load('res/3/4/5.txt'), b'789')
            with self.assertRaises(ValueError):
                rm.load('3/4/5.txt')

    def test_SaveLoadResources(self):
        with default_report_types({'MyReport': MyReportObject}), \
                TemporaryDirectory() as tempdir:
            rm = ResourceManager(tempdir)

            # test unsaved resources
            report = MyReportObject(
                children=[
                    Resource(data=b'123', extension='.c', name='child'),
                    Resource(data=b'456', content_type='image/png'),
                    Resource(data=b'789')
                ]
            )
            self.assertEqual(
                to_config(report),
                {'children': [
                    {'name': 'child', 'data': b'123', 'extension': '.c'},
                    {'data': b'456', 'content_type': 'image/png'},
                    {'data': b'789'}]}
            )

            # test save resources, as well as to_json / from_json
            report.assign_name_scopes()
            report.save_resources(rm)
            self.assertEqual(
                report.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "MyReport", "children": [{"__id__": 1, "__type__": "Resource", "extension": ".c", "name": "child", "name_scope": "my_report_object/child", "path": "my_report_object/child.c"}, {"__id__": 2, "__type__": "Resource", "content_type": "image/png", "name_scope": "my_report_object/resource", "path": "my_report_object/resource.png"}, {"__id__": 3, "__type__": "Resource", "name_scope": "my_report_object/resource_1", "path": "my_report_object/resource_1"}], "name_scope": "my_report_object"}'
            )
            self.assertEqual(
                repr(MyReportObject.from_json(report.to_json(sort_keys=True))),
                repr(report),
            )
            self.assertEqual(rm.load('my_report_object/child.c'), b'123')
            self.assertEqual(rm.load('my_report_object/resource.png'), b'456')
            self.assertEqual(rm.load('my_report_object/resource_1'), b'789')

            # test load resources
            report2 = MyReportObject.from_json(report.to_json(sort_keys=True))
            self.assertIsNone(report2.children[0].data)
            with TemporaryDirectory() as tempdir2, \
                    self.assertRaises(RuntimeError):
                report2.save_resources(ResourceManager(tempdir2))
            report2.load_resources(rm)
            self.assertEqual(report2.children[0].data, b'123')
            self.assertEqual(report2.children[1].data, b'456')
            self.assertEqual(report2.children[2].data, b'789')

            # test save and load gzip compressed data
            r = Resource(data=b'123', extension='.txt', gzip_compress=True)
            with TemporaryDirectory() as tempdir:
                r.assign_name_scopes()
                r.save_resources(ResourceManager(tempdir))
                self.assertEqual(
                    r.to_json(sort_keys=True),
                    '{"__id__": 0, "__type__": "Resource", "extension": ".txt", "gzip_compress": true, "name_scope": "resource", "path": "resource.txt"}'
                )
                r_path = os.path.join(tempdir, 'resource.txt.gz')
                self.assertTrue(os.path.exists(r_path))
                with gzip.open(r_path, 'rb') as f:
                    self.assertEqual(f.read(), b'123')

                r2 = Report.from_json(r.to_json(sort_keys=True))
                self.assertEqual(
                    r2.to_json(sort_keys=True),
                    '{"__id__": 0, "__type__": "Resource", "extension": ".txt", "gzip_compress": true, "name_scope": "resource", "path": "resource.txt"}'
                )
                r2.load_resources(ResourceManager(tempdir))
                self.assertEqual(r2.data, b'123')

if __name__ == '__main__':
    unittest.main()
