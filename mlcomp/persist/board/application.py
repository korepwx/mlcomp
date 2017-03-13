# -*- coding: utf-8 -*-
import re

import six
from flask import Flask

from mlcomp import __version__
from . import config
from .views import api_bp, main_bp, storage_bp
from .utils import MountTree
from .webpack import Webpack
from ..storage_tree import StorageTree, StorageTreeWatcher

__all__ = ['MainApp']


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


class MainApp(Flask):
    """The main application.

    Parameters
    ----------
    mappings : dict[str, str]
        Mappings from URL prefix to directory.
    """

    def __init__(self, mappings):
        super(MainApp, self).__init__(__name__)
        self.config.from_object(config)

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
        self.watcher = StorageTreeWatcher(six.itervalues(self.trees))
        self.watcher.start()

        # setup the plugins and views
        self.webpack = Webpack(self)
        self.register_blueprint(main_bp, url_prefix='')
        self.register_blueprint(api_bp, url_prefix='/_api')
        self.register_blueprint(storage_bp, url_prefix='/s')

        # inject Jinja2 template context
        self.jinja_env.globals.update({
            '__system__': SystemInfo()
        })
