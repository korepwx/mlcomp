# -*- coding: utf-8 -*-
import os
from logging import basicConfig

import six

from mlcomp.persist import Storage
from mlcomp.persist.board import config
from mlcomp.persist.board.application import MainApp
from mlcomp.report.demo import demo_report
from mlcomp.utils import TemporaryDirectory

basicConfig(level='DEBUG')

with TemporaryDirectory() as tempdir:
    f = lambda s: (
        s if isinstance(s, six.text_type) else s.decode('utf-8'))

    # populate the storage trees
    storage_dict = {}
    for name in ['a/1', 'a/2', 'a/b', 'b/1', 'b/2', 'c']:
        s = Storage(os.path.join(tempdir, name), mode='create')
        if name != 'c':
            s.description = name
            s.tags = [name, 'hello']
        storage_dict[name] = s

    # create a demo report under 'c'
    storage_dict['c'].save_report(demo_report())

    # construct the application
    config['DEBUG'] = True
    app = MainApp({
        '/': os.path.join(tempdir, 'a'),
        '/b/': os.path.join(tempdir, 'b'),
        '/c/': os.path.join(tempdir, 'c'),
    })

    with storage_dict['a/1'].with_context():
        app.run(debug=True, use_reloader=False, port=8888)
