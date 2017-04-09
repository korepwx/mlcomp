# -*- coding: utf-8 -*-
import json
import os
import re

import six
from flask import Flask

from mlcomp import __version__
from mlcomp.utils import object_to_dict
from . import config
from .views import api_bp, main_bp, storage_bp, report_bp
from .utils import MountTree
from .webpack import Webpack
from ..storage_tree import StorageTree, StorageTreeWatcher

__all__ = ['BoardApp', 'ReportApp']


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


class BoardApp(Flask):
    """The board application.

    Parameters
    ----------
    mappings : dict[str, str]
        Mappings from URL prefix to directory.
    """

    def __init__(self, mappings):
        super(BoardApp, self).__init__(__name__)
        self.config.from_mapping(config)

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
            '__system__': SystemInfo(),
        })


class ReportApp(Flask):
    """The single report file application.

    Parameters
    ----------
    report_dir : str
        The path of the report directory (which contains "report.json").
    """

    def __init__(self, report_dir):
        super(ReportApp, self).__init__(__name__)
        self.config.from_mapping(config)

        # check the report directory
        self.report_dir = os.path.abspath(report_dir)

        # setup the plugins and views
        self.webpack = Webpack(self)
        self.register_blueprint(report_bp, url_prefix='')

        # inject Jinja2 template context
        self.jinja_env.globals.update({
            '__system__': SystemInfo(),
        })
