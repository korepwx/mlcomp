# -*- coding: utf-8 -*-
import codecs
import os
import time
import unittest

from mlcomp.persist import Storage, StorageReadOnlyError
from mlcomp.persist.storage import STORAGE_META_FILE, STORAGE_RUNNING_STATUS
from mlcomp.report import Text
from mlcomp.utils import TemporaryDirectory


def writefile(path, cnt):
    with codecs.open(path, 'wb', 'utf-8') as f:
        f.write(cnt)


def readfile(path):
    with codecs.open(path, 'rb', 'utf-8') as f:
        return f.read()


def list_dir_contents(path):
    def discover(p):
        if os.path.isdir(p):
            return {
                fname: discover(os.path.join(p, fname))
                for fname in os.listdir(p)
            }
        else:
            return readfile(p)
    return discover(os.path.abspath(path))


class StorageTestCase(unittest.TestCase):
    """Test cases for storage."""

    META_ATTRS = ('description', 'tags')

    def test_basic(self):
        with TemporaryDirectory() as tempdir:
            # test to create a new storage
            s_path = os.path.join(tempdir, 'a')
            s1 = Storage(s_path, mode='create')
            s_meta_file = os.path.join(s_path, STORAGE_META_FILE)
            self.assertTrue(os.path.isfile(s_meta_file))

            # create an existing storage will cause an error
            with self.assertRaises(IOError):
                Storage(s_path, mode='create')

            # test to set the meta information of the storage
            s1.description = 'description'
            s1.tags = ['tag1', 'tag2']
            with self.assertRaises(StorageReadOnlyError):
                s1.create_time = 123

            # test to open a storage for read
            s2 = Storage(s_path, mode='read')
            for attr in self.META_ATTRS:
                self.assertEqual(getattr(s2, attr), getattr(s1, attr))
            with self.assertRaises(StorageReadOnlyError):
                s2.description = 'description2'
            with self.assertRaises(StorageReadOnlyError):
                s2.tags = ['tag3']
            with self.assertRaises(StorageReadOnlyError):
                s2.tags.add('tag3')

            # test to open a storage for write
            s3 = Storage(s_path, mode='write')
            for attr in self.META_ATTRS:
                self.assertEqual(getattr(s3, attr), getattr(s1, attr))
            s3.description = 'description3'
            s3.tags = ['tag1', 'tag2', 'tag3']
            s3.tags.add('tag4')
            s3.tags.remove('tag2')
            self.assertEqual(s3.description, 'description3')
            self.assertEqual(s3.tags, ['tag1', 'tag3', 'tag4'])

            s4 = Storage(s_path, mode='read')
            for attr in self.META_ATTRS:
                self.assertEqual(getattr(s4, attr), getattr(s3, attr))

            # test reload
            s1.reload()
            for attr in self.META_ATTRS:
                self.assertEqual(getattr(s1, attr), getattr(s4, attr))

            # test keep running status
            status_file = os.path.join(s_path, STORAGE_RUNNING_STATUS)
            self.assertIsNone(s3.running_status)
            self.assertFalse(os.path.exists(status_file))

            with s3.keep_running_status():
                self.assertIsNotNone(s3.running_status)
                self.assertTrue(os.path.isfile(status_file))
                time.sleep(0.1)
                s1.reload()
                self.assertIsNotNone(s1.running_status)
                self.assertEqual(s1.running_status, s3.running_status)

            self.assertIsNone(s3.running_status)
            self.assertFalse(os.path.exists(status_file))
            s1.reload()
            self.assertIsNone(s1.running_status)

    def test_save_script(self):
        with TemporaryDirectory() as tempdir:
            s = Storage(os.path.join(tempdir, 's'), mode='create')

            # test copy script
            script_path = os.path.join(tempdir, '1.py')
            writefile(script_path, 'print("hello, world")')
            s.save_script(script_path)
            self.assertEqual(
                list_dir_contents(s.resolve_path('script')),
                {'1.py': 'print("hello, world")'}
            )

            # test copy script directory
            os.makedirs(os.path.join(tempdir, '2/3'))
            os.makedirs(os.path.join(tempdir, '2/.git'))
            writefile(os.path.join(tempdir, '2/a.py'), 'print(123)')
            writefile(os.path.join(tempdir, '2/3/b.py'), 'print(456)')
            writefile(os.path.join(tempdir, '2/.git/c.py'), 'print(789)')

            s.save_script(os.path.join(tempdir, '2'))
            self.assertEqual(
                list_dir_contents(s.resolve_path('script')),
                {'a.py': 'print(123)',
                 '3': {'b.py': 'print(456)'}}
            )

            # test copy without exclude
            s.save_script(os.path.join(tempdir, '2'), excludes=None)
            self.assertEqual(
                list_dir_contents(s.resolve_path('script')),
                {'a.py': 'print(123)',
                 '3': {'b.py': 'print(456)'},
                 '.git': {'c.py': 'print(789)'}}
            )

    def test_copy_files(self):
        with TemporaryDirectory() as tempdir:
            s = Storage(os.path.join(tempdir, 's'), mode='create')

            # test copy file without overwrite
            script_path = os.path.join(tempdir, '1.py')
            writefile(script_path, 'print("hello, world")')
            s.copy_file(script_path, 'a/1.py', overwrite=False)
            self.assertEqual(
                list_dir_contents(s.resolve_path('a')),
                {'1.py': 'print("hello, world")'}
            )
            with self.assertRaises(IOError):
                s.copy_file(script_path, 'a/1.py', overwrite=False)

            # test copy file with overwrite
            writefile(script_path, 'print("apple")')
            s.copy_file(script_path, 'a/1.py', overwrite=True)
            self.assertEqual(
                list_dir_contents(s.resolve_path('a')),
                {'1.py': 'print("apple")'}
            )

            # test copy directory without overwrite
            os.makedirs(os.path.join(tempdir, '2/3'))
            os.makedirs(os.path.join(tempdir, '2/.git'))
            writefile(os.path.join(tempdir, '2/a.py'), 'print(123)')
            writefile(os.path.join(tempdir, '2/3/b.py'), 'print(456)')
            writefile(os.path.join(tempdir, '2/.git/c.py'), 'print(789)')

            s.copy_dir(os.path.join(tempdir, '2'), '3/4', overwrite=False)
            self.assertEqual(
                list_dir_contents(s.resolve_path('3/4')),
                {'a.py': 'print(123)',
                 '3': {'b.py': 'print(456)'}}
            )
            with self.assertRaises(IOError):
                s.copy_dir(os.path.join(tempdir, '2'), '3/4', overwrite=False)

            # test copy directory without excludes
            s.copy_dir(os.path.join(tempdir, '2'), '5/6', overwrite=False,
                       excludes=None)
            self.assertEqual(
                list_dir_contents(s.resolve_path('5/6')),
                {'a.py': 'print(123)',
                 '3': {'b.py': 'print(456)'},
                 '.git': {'c.py': 'print(789)'}}
            )
            with self.assertRaises(IOError):
                s.copy_dir(os.path.join(tempdir, '2'), '5/6', overwrite=False)

            # test copy directory with overwrite
            os.makedirs(os.path.join(tempdir, '3/6'))
            writefile(os.path.join(tempdir, '3/x.py'), 'print(987)')
            writefile(os.path.join(tempdir, '3/6/y.py'), 'print(654)')

            s.copy_dir(os.path.join(tempdir, '3'), '3/4', overwrite=True)
            self.assertEqual(
                list_dir_contents(s.resolve_path('3/4')),
                {'x.py': 'print(987)',
                 '6': {'y.py': 'print(654)'}}
            )

    def test_save_report(self):
        with TemporaryDirectory() as tempdir:
            s = Storage(os.path.join(tempdir, 's'), mode='create')
            s.save_report(Text('hello, world'))
            s.save_report(Text('hi, google'), dir_name='test')
            self.assertEqual(
                list_dir_contents(s.resolve_path('report')),
                {
                    'default': {
                        'report.json': '{"generator": "mlcomp 0.1", '
                                       '"report": {"__id__": 0, '
                                       '"__type__": "Text", "name_scope": '
                                       '"text", "text": "hello, world"}}'
                    },
                    'test': {
                        'report.json': '{"generator": "mlcomp 0.1", '
                                       '"report": {"__id__": 0, '
                                       '"__type__": "Text", "name_scope": '
                                       '"text", "text": "hi, google"}}'
                    }
                }
            )
            self.assertEqual(s.list_reports(), ['default', 'test'])

if __name__ == '__main__':
    unittest.main()
