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
            s1 = sg.create_storage(hostname='host1')
            self.assertTrue(s1.name.startswith('host1__'))
            s1_2 = sg.create_storage(hostname='host1')
            self.assertTrue(s1_2.name.startswith('host1__'))
            self.assertNotEquals(s1.name, s1_2.name)
            time.sleep(0.01)
            s2 = sg.create_storage('abc', hostname='host1')
            self.assertTrue(s2.name.startswith('abc__host1__'))
            time.sleep(0.01)
            s3 = sg.create_storage(hostname='host__2')
            self.assertTrue(s3.name.startswith('host_2__'))
            time.sleep(0.01)
            s4 = sg.create_storage('abc', hostname='host__2')
            self.assertTrue(s4.name.startswith('abc__host_2__'))
            time.sleep(0.01)
            sbad = Storage(os.path.join(tempdir, 'badname'), mode='create')
            self.assertEquals(sbad.name, 'badname')

            # test match
            self.assertEquals(
                sorted(sg.iter_storage()),
                [s2.name, s4.name, s1.name, s1_2.name, s3.name]
            )
            self.assertEquals(
                sorted(sg.iter_storage(well_named=False)),
                [s2.name, s4.name, sbad.name, s1.name, s1_2.name, s3.name]
            )
            self.assertEquals(
                sorted(sg.iter_storage(hostname='host1')),
                [s2.name, s1.name, s1_2.name]
            )
            self.assertEquals(
                sorted(sg.iter_storage(hostname='host1', well_named=False)),
                [s2.name, s1.name, s1_2.name]
            )
            self.assertEquals(
                sorted(sg.iter_storage(hostname='host__2')),
                [s4.name, s3.name]
            )
            self.assertEquals(
                sorted(sg.iter_storage(hostname='host3')),
                []
            )

            # test find latest
            self.assertEquals(sg.open_latest_storage().name, s4.name)
            self.assertEquals(sg.open_latest_storage('host1').name, s2.name)
            self.assertEquals(sg.open_latest_storage('host__2').name, s4.name)
            self.assertIsNone(sg.open_latest_storage('host3'))
