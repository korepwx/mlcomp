# -*- coding: utf-8 -*-
import codecs
import os
import time
import unittest

from mlcomp.persist import Storage, StorageReadOnlyError
from mlcomp.persist.storage import STORAGE_META_FILE, STORAGE_RUNNING_STATUS
from mlcomp.utils import TemporaryDirectory


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
        def writefile(path, cnt):
            with codecs.open(path, 'wb', 'utf-8') as f:
                f.write(cnt)

        def readfile(path):
            with codecs.open(path, 'rb', 'utf-8') as f:
                return f.read()

        with TemporaryDirectory() as tempdir:
            s = Storage(os.path.join(tempdir, 's'), mode='create')

            # test copy script
            script_path = os.path.join(tempdir, '1.py')
            script_content = 'print("hello, world")'
            writefile(script_path, script_content)
            s.save_script(script_path)
            s_script_path = os.path.join(s.path, 'script/1.py')
            self.assertTrue(os.path.isfile(s_script_path))
            self.assertEqual(readfile(s_script_path), script_content)

            # test copy script directory
            os.makedirs(os.path.join(tempdir, '2/3'))
            os.makedirs(os.path.join(tempdir, '2/.git'))
            writefile(os.path.join(tempdir, '2/a.py'), 'print(123)')
            writefile(os.path.join(tempdir, '2/3/b.py'), 'print(456)')
            writefile(os.path.join(tempdir, '2/.git/c.py'), 'print(789)')

            s.save_script(os.path.join(tempdir, '2'))
            s_a_script_path = os.path.join(s.path, 'script/a.py')
            s_b_script_path = os.path.join(s.path, 'script/3/b.py')
            s_git_path = os.path.join(s.path, 'script/.git')
            s_c_script_path = os.path.join(s.path, 'script/.git/c.py')
            self.assertTrue(os.path.isfile(s_a_script_path))
            self.assertTrue(os.path.isfile(s_b_script_path))
            self.assertFalse(os.path.isdir(s_git_path))
            self.assertFalse(os.path.isfile(s_c_script_path))
            self.assertEqual(readfile(s_a_script_path), 'print(123)')
            self.assertEqual(readfile(s_b_script_path), 'print(456)')

            # test copy without exclude
            s.save_script(os.path.join(tempdir, '2'), excludes=None)
            self.assertTrue(os.path.isfile(s_c_script_path))
            self.assertEqual(readfile(s_c_script_path), 'print(789)')

if __name__ == '__main__':
    unittest.main()
