# -*- coding: utf-8 -*-
import re

import six
from flask import Flask
from flask_autoindex import AutoIndex
from logging import getLogger
from werkzeug.wsgi import pop_path_info

from .views import api_bp, main_bp, storage_bp
from .utils import MountTree
from ..storage_tree import StorageTree, StorageTreeWatcher

if six.PY2:
    from urlparse import quote as urlquote
else:
    from urllib.parse import quote as urlquote

__all__ = ['MainApp']


def norm_url_prefix(url):
    """Normalize the url prefix."""
    url = re.sub(r'[/\\]+', '/', url).rstrip('/')
    if url != '' and not url.startswith(''):
        url = '/' + url
    if url == '/_api':
        raise ValueError('URL prefix of a storage cannot be `/_api`.')
    return url


def get_request_path(environ):
    """Get the request path from wsgi environ dict."""
    def unquote(s):
        return urlquote(s, safe='/;=,', encoding='latin1')

    path = unquote(environ.get('SCRIPT_NAME', '')).rstrip('/')
    path += unquote(environ.get('PATH_INFO', ''))
    if not path.startswith('/'):
        path = '/' + path
    return path


class MainApp(Flask):
    """The main application.

    Parameters
    ----------
    mappings : dict[str, str]
        Mappings from URL prefix to directory.
    """

    def __init__(self, mappings):

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
        self.watcher = StorageTreeWatcher(six.itervalues(self.trees))
        self.watcher.start()

        # initialize the Flask application.
        super(MainApp, self).__init__(__name__)
        self.register_blueprint(main_bp, url_prefix='')
        self.register_blueprint(api_bp, url_prefix='/_api')

        # setup the storage applications and the dispatcher
        self.mount_tree = MountTree()
        for url, tree in six.iteritems(self.trees):
            self.mount_tree.mount(url, StorageApp(tree))

        # fix the '/_api' mount point.
        self.mount_tree.mount('/_api', self)

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']

        # special treatment for the main application:
        # the index page should always be served by the main app.
        if path_info != '/':
            node = self.mount_tree.get_node(path_info, use_parent=True)
            app = node.data
            if app and app is not self:
                count = len([v for v in node.path.split('/') if v])
                for i in range(count):
                    pop_path_info(environ)
                getLogger(__name__).info('dispatch %r to %r.', path_info, app)
                return app(environ, start_response)
        return super(MainApp, self).__call__(environ, start_response)


class StorageApp(Flask):
    """The per-storage application.

    Parameters
    ----------
    tree : StorageTree
        The storage tree object for this application.
    """

    def __init__(self, tree):
        self.tree = tree

        # initialize the Flask application
        super(StorageApp, self).__init__(__name__)
        self.register_blueprint(storage_bp, url_prefix='')
        self.auto_index = AutoIndex(self, self.tree_path, add_url_rules=True)

    @property
    def tree_path(self):
        return self.tree.root.path

    def __repr__(self):
        return 'StorageApp(%r)' % (self.tree_path,)
