# -*- coding: utf-8 -*-
import os
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
                self.assertEquals(getattr(s2, attr), getattr(s1, attr))
            with self.assertRaises(StorageReadOnlyError):
                s2.description = 'description2'
            with self.assertRaises(StorageReadOnlyError):
                s2.tags = ['tag3']
            with self.assertRaises(StorageReadOnlyError):
                s2.tags.add('tag3')

            # test to open a storage for write
            s3 = Storage(s_path, mode='write')
            for attr in self.META_ATTRS:
                self.assertEquals(getattr(s3, attr), getattr(s1, attr))
            s3.description = 'description3'
            s3.tags = ['tag1', 'tag2', 'tag3']
            s3.tags.add('tag4')
            s3.tags.remove('tag2')
            self.assertEquals(s3.description, 'description3')
            self.assertEquals(s3.tags, ['tag1', 'tag3', 'tag4'])

            s4 = Storage(s_path, mode='read')
            for attr in self.META_ATTRS:
                self.assertEquals(getattr(s4, attr), getattr(s3, attr))

            # test reload
            s1.reload()
            for attr in self.META_ATTRS:
                self.assertEquals(getattr(s1, attr), getattr(s4, attr))

            # test keep running status
            status_file = os.path.join(s_path, STORAGE_RUNNING_STATUS)
            self.assertIsNone(s3.running_status)
            self.assertFalse(os.path.exists(status_file))

            with s3.keep_running_status():
                self.assertIsNotNone(s3.running_status)
                self.assertTrue(os.path.isfile(status_file))
                s1.reload()
                self.assertIsNotNone(s1.running_status)
                self.assertEquals(s1.running_status, s3.running_status)

            self.assertIsNone(s3.running_status)
            self.assertFalse(os.path.exists(status_file))
            s1.reload()
            self.assertIsNone(s1.running_status)
