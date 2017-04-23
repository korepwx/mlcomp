# -*- coding: utf-8 -*-
import codecs
import json
import os
import unittest

import six

from mlcomp.board.application import BoardApp
from mlcomp.persist import Storage
from mlcomp.utils import TemporaryDirectory, is_windows


class ViewsTestCase(unittest.TestCase):
    """Test cases for views."""

    @unittest.skipIf(is_windows(), 'MLComp Board does not support Windows yet.')
    def test_routes(self):
        with TemporaryDirectory() as tempdir:
            f = lambda s: (
                s if isinstance(s, six.text_type) else s.decode('utf-8'))

            def read_meta(storage):
                with codecs.open(
                        storage.resolve_path('storage.json'),
                        'rb',
                        'utf-8') as f_meta:
                    return f_meta.read()

            # populate the storage trees
            storage_dict = {}
            for name in ['a/1', 'a/2', 'a/b', 'b/1', 'b/2', 'c']:
                s = Storage(os.path.join(tempdir, name), mode='create')
                s.description = name
                storage_dict[name] = s

            # construct the application
            app = BoardApp({
                '/': os.path.join(tempdir, 'a'),
                '/b/': os.path.join(tempdir, 'b'),
                '/c/': os.path.join(tempdir, 'c'),
            })

            # test the routes
            with app.test_client() as c:
                # test the main routes
                rv = c.get('/_hello/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(f(rv.data), 'main hello')

                # test the api routes
                rv = c.get('/_api/_hello/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(f(rv.data).strip(), '"api hello"')

                # test the storage routes
                rv = c.get('/s/_hello/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(f(rv.data), 'storage hello')

                rv = c.get('/s/1/_greeting/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    f(rv.data),
                    'storage greeting\n%s\n1\n' % (storage_dict['a/1'].path,)
                )

                rv = c.get('/s/1/storage.json')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(f(rv.data), read_meta(storage_dict['a/1']))

                rv = c.get('/s/2/_greeting/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    f(rv.data),
                    'storage greeting\n%s\n2\n' % (storage_dict['a/2'].path,)
                )

                rv = c.get('/s/b/_greeting/')
                self.assertEqual(rv.status_code, 404)

                rv = c.get('/s/b/storage.json')
                self.assertEqual(rv.status_code, 404)

                rv = c.get('/s/b/1/_greeting/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    f(rv.data),
                    'storage greeting\n%s\nb/1\n' % (storage_dict['b/1'].path,)
                )

                rv = c.get('/s/b/1/storage.json')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(f(rv.data), read_meta(storage_dict['b/1']))

                rv = c.get('/s/b/2/_greeting/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    f(rv.data),
                    'storage greeting\n%s\nb/2\n' % (storage_dict['b/2'].path,)
                )

                rv = c.get('/s/c/_greeting/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    f(rv.data),
                    'storage greeting\n%s\nc\n' % (storage_dict['c'].path,)
                )

                rv = c.get('/s/c/storage.json')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(f(rv.data), read_meta(storage_dict['c']))

    @unittest.skipIf(is_windows(), 'MLComp Board does not support Windows yet.')
    def test_tree_root_as_storage(self):
        with TemporaryDirectory() as tempdir:
            f = lambda s: (
                s if isinstance(s, six.text_type) else s.decode('utf-8'))

            # populate the storage tree
            os.removedirs(tempdir)
            s = Storage(tempdir, mode='create')

            # construct the application
            app = BoardApp({'/': tempdir})

            with app.test_client() as c:
                # test the routes
                rv = c.get('/s/_greeting/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    f(rv.data),
                    'storage greeting\n%s\n\n' % (s.path,)
                )

                rv = c.get('/s/storage.json')
                self.assertEqual(rv.status_code, 200)
                with codecs.open(s.resolve_path('storage.json'),
                                 'rb', 'utf-8') as fin:
                    self.assertEqual(f(rv.data), fin.read())

                # test the api output
                rv = c.get('/_api/all')
                self.assertEqual(rv.status_code, 200)
                cnt = json.loads(f(rv.data))
                self.assertIsInstance(cnt, dict)
                self.assertIn('create_time', cnt)
                self.assertIn('update_time', cnt)
