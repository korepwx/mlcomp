# -*- coding: utf-8 -*-
import os
import unittest

import time

from mlcomp.persist import StorageGroup, Storage
from mlcomp.utils import TemporaryDirectory


class StorageGroupTestCase(unittest.TestCase):

    def test_match_name(self):
        with TemporaryDirectory() as tempdir:
            sg = StorageGroup(tempdir)

            # test create
            s0 = sg.create_storage()
            self.assertTrue('__' not in s0.name)
            s1 = sg.create_storage(hostname='host1')
            self.assertTrue(s1.name.endswith('__host1'))
            s1_2 = sg.create_storage(hostname='host1')
            self.assertTrue(s1_2.name.endswith('__host1'))
            self.assertNotEquals(s1.name, s1_2.name)
            time.sleep(0.01)
            s2 = sg.create_storage('abc', hostname='host1')
            self.assertTrue(s2.name.startswith('abc__'))
            self.assertTrue(s2.name.endswith('__host1'))
            time.sleep(0.01)
            s3 = sg.create_storage(hostname='host__2')
            self.assertTrue(s3.name.endswith('__host_2'))
            time.sleep(0.01)
            s4 = sg.create_storage('abc', hostname='host__2')
            self.assertTrue(s4.name.startswith('abc__'))
            self.assertTrue(s4.name.endswith('__host_2'))
            time.sleep(0.01)
            sbad = Storage(os.path.join(tempdir, 'badname'), mode='create')
            self.assertEqual(sbad.name, 'badname')

            # test match
            f = lambda *args, **kwargs: (
                sorted(str(s) for s in sg.iter_storage(*args, **kwargs))
            )
            self.assertEqual(
                f(),
                [s0.name, s1.name, s1_2.name, s3.name, s2.name, s4.name]
            )
            self.assertEqual(
                f(well_defined=False),
                [s0.name, s1.name, s1_2.name, s3.name, s2.name, s4.name,
                 sbad.name]
            )
            self.assertEqual(
                f(hostname='host1'),
                [s1.name, s1_2.name, s2.name]
            )
            self.assertEqual(
                f(hostname='host1', well_defined=False),
                [s1.name, s1_2.name, s2.name]
            )
            self.assertEqual(
                f(hostname='host__2'),
                [s3.name, s4.name]
            )
            self.assertEqual(
                f(hostname='host3'),
                []
            )

            # test find latest
            self.assertEqual(sg.open_latest_storage().name, s4.name)
            self.assertEqual(sg.open_latest_storage('host1').name, s2.name)
            self.assertEqual(sg.open_latest_storage('host__2').name, s4.name)
            self.assertIsNone(sg.open_latest_storage('host3'))
