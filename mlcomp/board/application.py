# -*- coding: utf-8 -*-
import json
import os
import re
from contextlib import contextmanager

import six
from flask import Flask

from mlcomp import __version__
from mlcomp.persist import Storage
from mlcomp.persist.storage_tree import StorageTree, StorageTreeWatcher
from mlcomp.utils import object_to_dict, is_windows, BackgroundWorker
from . import config
from .views import api_bp, main_bp, storage_bp, report_bp
from .utils import MountTree
from .webpack import Webpack

__all__ = ['BoardApp', 'StorageApp', 'ReportApp']


def norm_url_prefix(url):
    """Normalize the url prefix."""
    url = re.sub(r'[/\\]+', '/', url).rstrip('/')
    if url != '' and not url.startswith(''):
        url = '/' + url
    if url == '/_api':
        raise ValueError('URL prefix of a storage cannot be `/_api`.')
    return url


class SystemInfo(object):

    def __init__(self):
        self.name = 'ML Companion'
        self.version = __version__

    def to_json(self):
        return json.dumps(object_to_dict(self))


class BaseApp(Flask):

    def __init__(self):
        super(BaseApp, self).__init__(__name__)
        self.config.from_mapping(config)
        self.webpack = Webpack(self)
        self.jinja_env.globals.update({
            '__system__': SystemInfo(),
        })

    @contextmanager
    def with_context(self):
        """Open the context to serve this application."""
        yield self


class BoardApp(BaseApp):
    """The board application.

    Parameters
    ----------
    mappings : dict[str, str]
        Mappings from URL prefix to directory.

    disable_watcher : bool
        Whether or not to disable the file system watcher? (default False)
    """

    def __init__(self, mappings, disable_watcher=False):
        if not disable_watcher and is_windows():
            raise RuntimeError('MLComp Board does not support watching file '
                               'system changes on windows yet.')
        super(BoardApp, self).__init__()

        # check the mappings
        self.mappings = {
            norm_url_prefix(url): path
            for url, path in six.iteritems(mappings)
        }

        # build the storage tree and watcher
        self.trees = {
            url: StorageTree(path)
            for url, path in six.iteritems(self.mappings)
        }
        self.mounts = MountTree()
        for url, tree in six.iteritems(self.trees):
            self.mounts.mount(url, tree)
        if disable_watcher:
            self.watcher = None
        else:
            self.watcher = StorageTreeWatcher(six.itervalues(self.trees))
            self.watcher.start()

        # setup the plugins and views
        self.register_blueprint(main_bp, url_prefix='')
        self.register_blueprint(api_bp, url_prefix='/_api')
        self.register_blueprint(storage_bp, url_prefix='/s')

    @property
    def is_board_app(self):
        """This method is provided for `storage_bp`."""
        return True


class StorageApp(BaseApp):
    """The single storage application.

    Parameters
    ----------
    storage_dir : str
        The path of the storage directory (which contains "storage.json").

    disable_watcher : bool
        Whether or not to disable the file system watcher? (default False)
    """

    def __init__(self, storage_dir, disable_watcher=False):
        super(StorageApp, self).__init__()

        # open the storage
        self.storage_dir = os.path.abspath(storage_dir)
        self.storage = Storage(self.storage_dir, mode='read')

        # setup the plugins and views
        self.register_blueprint(storage_bp, url_prefix='')

    @property
    def is_board_app(self):
        """This method is provided for `storage_bp`."""
        return False

    @contextmanager
    def with_context(self):
        worker = BackgroundWorker(self.storage.reload, sleep_seconds=1)
        try:
            worker.start()
            yield self
        finally:
            worker.stop()


class ReportApp(BaseApp):
    """The single report file application.

    Parameters
    ----------
    report_dir : str
        The path of the report directory (which contains "report.json").

    disable_watcher : bool
        Whether or not to disable the file system watcher? (default False)
    """

    def __init__(self, report_dir, disable_watcher=False):
        super(ReportApp, self).__init__()

        # check the report directory
        self.report_dir = os.path.abspath(report_dir)

        # setup the plugins and views
        self.register_blueprint(report_bp, url_prefix='')
