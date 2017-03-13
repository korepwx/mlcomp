# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import itertools

from mlcomp.persist import Storage
from mlcomp.persist.storage_tree import StorageTree
from mlcomp.utils import TemporaryDirectory


class StorageTreeTestCase(unittest.TestCase):
    """Test cases for StorageTree."""

    def populate_tree(self, path, level, width=3):
        for seq in itertools.product(*([list(range(width))] * level)):
            p = os.path.join(path, '/'.join(str(s) for s in seq))
            Storage(p, 'create')

    def test_tree(self):
        """Test the basic functions of a tree."""
        with TemporaryDirectory() as tempdir:
            # test to construct the tree
            self.populate_tree(tempdir, 2, width=2)
            tree = StorageTree(tempdir)
            names = ['0/0', '0/1', '1/0', '1/1']
            self.assertEquals(
                [k for k, v in tree.iter_storage()],
                names
            )
            for k, v in tree.iter_storage():
                self.assertTrue(os.path.samefile(
                    os.path.join(tempdir, k),
                    v.path
                ))
            storage_dict = {
                k: v for k, v in tree.iter_storage()
            }

            # test find the nodes
            for name in names:
                self.assertEquals(tree.find_storage(name), storage_dict[name])
            self.assertIsNone(tree.find_storage('0/999'))
            self.assertIsNone(tree.find_storage('999'))
            self.assertIsNone(tree.find_storage(''))

            # test to reload a storage
            s = Storage(os.path.join(tempdir, '0/0'), 'write')
            s.description = '0/0 description'
            self.assertIsNone(tree.find_storage('0/0').description)
            tree.set_reload('0/0')
            self.assertEquals(tree.find_storage('0/0').description,
                              '0/0 description')

            # test to reload a renamed storage
            os.rename(
                os.path.join(tempdir, '0/0'),
                os.path.join(tempdir, '1/2')
            )
            tree.set_reload('0')
            tree.set_reload('1')
            self.assertEquals(
                [k for k, v in tree.iter_storage()],
                ['0/1', '1/0', '1/1', '1/2']
            )

            # test to reload created storage
            Storage(os.path.join(tempdir, '0/0/0'), 'create')
            Storage(os.path.join(tempdir, '0/0/1'), 'create')
            tree.set_reload('0/0')
            self.assertEquals(
                [k for k, v in tree.iter_storage()],
                ['0/0/0', '0/0/1', '0/1', '1/0', '1/1', '1/2']
            )

            # test to reload deleted storage
            shutil.rmtree(os.path.join(tempdir, '0/0'))
            shutil.rmtree(os.path.join(tempdir, '1/2'))
            tree.set_reload('0')
            tree.set_reload('1')
            self.assertEquals(
                [k for k, v in tree.iter_storage()],
                ['0/1', '1/0', '1/1']
            )
