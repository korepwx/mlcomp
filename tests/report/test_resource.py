# -*- coding: utf-8 -*-
import copy
import unittest

from mlcomp.report import (Resource, ResourceManager, ReportObject,
                           default_report_types)
from mlcomp.utils import TemporaryDirectory


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
                rm.save('', 'x', extension='')

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

            # test to_json / from_json of unsaved resources
            report = MyReportObject(
                children=[
                    Resource(data=b'123', extension='.c', name='child'),
                    Resource(data=b'456', content_type='image/png'),
                    Resource(data=b'789')
                ]
            )
            self.assertEqual(
                report.to_json(),
                '{"children": [{"name": "child", "data": {"__type__": "binary", "data": "MTIz", "__id__": 2}, "extension": ".c", "__type__": "Resource", "__id__": 1}, {"data": {"__type__": "binary", "data": "NDU2", "__id__": 4}, "content_type": "image/png", "__type__": "Resource", "__id__": 3}, {"data": {"__type__": "binary", "data": "Nzg5", "__id__": 6}, "__type__": "Resource", "__id__": 5}], "__type__": "MyReport", "__id__": 0}'
            )
            self.assertEqual(
                repr(MyReportObject.from_json(report.to_json())),
                repr(report),
            )

            # test save resources, as well as to_json / from_json
            report.assign_name_scopes()
            report.save_resources(rm)
            self.assertEqual(
                report.to_json(),
                '{"name_scope": "my_report_object", "children": [{"name": "child", "name_scope": "my_report_object/child", "path": "my_report_object/child.c", "extension": ".c", "__type__": "Resource", "__id__": 1}, {"name_scope": "my_report_object/resource", "path": "my_report_object/resource.png", "content_type": "image/png", "__type__": "Resource", "__id__": 2}, {"name_scope": "my_report_object/resource_1", "path": "my_report_object/resource_1", "__type__": "Resource", "__id__": 3}], "__type__": "MyReport", "__id__": 0}'
            )
            self.assertEqual(
                repr(MyReportObject.from_json(report.to_json())),
                repr(report),
            )
            self.assertEqual(rm.load('my_report_object/child.c'), b'123')
            self.assertEqual(rm.load('my_report_object/resource.png'), b'456')
            self.assertEqual(rm.load('my_report_object/resource_1'), b'789')

            # test load resources
            report2 = MyReportObject.from_json(report.to_json())
            self.assertIsNone(report2.children[0].data)
            with TemporaryDirectory() as tempdir2, \
                    self.assertRaises(RuntimeError):
                report2.save_resources(ResourceManager(tempdir2))
            report2.load_resources(rm)
            self.assertEqual(report2.children[0].data, b'123')
            self.assertEqual(report2.children[1].data, b'456')
            self.assertEqual(report2.children[2].data, b'789')


if __name__ == '__main__':
    unittest.main()