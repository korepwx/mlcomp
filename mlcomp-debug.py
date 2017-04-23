# -*- coding: utf-8 -*-
import os
from logging import basicConfig

import six

from mlcomp.board import config
from mlcomp.board.application import BoardApp, ReportApp, StorageApp
from mlcomp.persist import Storage
from mlcomp.report import Text
from mlcomp.report.demo import demo_report
from mlcomp.utils import TemporaryDirectory

config['DEBUG'] = True
basicConfig(level='DEBUG')


def debug_board():
    with TemporaryDirectory() as tempdir:
        print(tempdir)
        f = lambda s: (
            s if isinstance(s, six.text_type) else s.decode('utf-8'))

        # populate the storage trees
        storage_dict = {}
        for name in ['a/1', 'a/2', 'a/b', 'b/1', 'b/2', 'c']:
            s = Storage(os.path.join(tempdir, name), mode='create')
            if name != 'b/1':
                s.description = name
                s.tags = [name, 'hello']
            storage_dict[name] = s

        # create a demo report under 'c'
        storage_dict['c'].save_report(demo_report())
        storage_dict['c'].save_report(
            Text('This is the test report.'),
            'test'
        )

        # run the debug server
        config['DEBUG'] = True
        storage_dict['c'].save_script(__file__)
        with storage_dict['c'].with_context():
            app = BoardApp({
                '/': os.path.join(tempdir, 'a'),
                '/b/': os.path.join(tempdir, 'b'),
                '/c/': os.path.join(tempdir, 'c'),
            })
            with app.with_context():
                app.run(debug=True, use_reloader=False, port=8888)


def debug_storage():
    with TemporaryDirectory() as tempdir:
        print(tempdir)
        f = lambda s: (
            s if isinstance(s, six.text_type) else s.decode('utf-8'))

        # populate the storage trees
        s = Storage(tempdir + '/1', mode='create')

        # create a demo report
        s.save_report(demo_report())
        s.save_report(
            Text('This is the test report.'),
            'test'
        )

        # run the debug server
        config['DEBUG'] = True
        s.save_script(__file__)
        with s.with_context():
            app = StorageApp(s.path)
            with app.with_context():
                app.run(debug=True, use_reloader=False, port=8888)


def debug_report():
    with TemporaryDirectory() as tempdir:
        print(tempdir)
        r = demo_report()
        r.title = None
        r.save(tempdir)
        app = ReportApp(tempdir)
        with app.with_context():
            app.run(debug=True, use_reloader=False, port=8888)


if __name__ == '__main__':
    debug_board()
    # debug_storage()
    # debug_report()
