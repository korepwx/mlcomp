# -*- coding: utf-8 -*-
import os

import six
from flask import Blueprint, request, current_app
from werkzeug.exceptions import NotFound


storage_bp = Blueprint('storage', __name__.rsplit('.')[1])


def parse_request_storage(method):
    """Decorator that parses the request path to find the storage.

    The storage as well as the request path inside the storage will
    be passed to the method as named argument `storage` and `path`.
    """
    @six.wraps(method)
    def wrapped(*args, **kwargs):
        # first, find the tree and get the path in the tree
        path = kwargs.pop('path')
        node = current_app.mounts.get_node(path, use_parent=True)
        if not node or not node.data:
            raise NotFound()
        pop_items = [v for v in node.path.split('/') if v]
        for i in range(len(pop_items)):
            if not path:
                raise NotFound()
            path = path.lstrip('/')
            pos = path.find('/')
            if pos >= 0:
                path = path[pos+1:]
            else:
                path = ''
        # now we've get the path inside the tree, continue to get the storage
        tree = node.data
        storage = tree.find_storage(path)
        if not storage:
            raise NotFound()
        # and get the path inside the storage
        path = os.path.abspath(os.path.join(tree.path, path))
        path = os.path.relpath(storage.path, path).replace('\\', '/')
        # finally, call the method
        kwargs.setdefault('storage', storage)
        kwargs.setdefault('path', path)
        return method(*args, **kwargs)
    return wrapped


@storage_bp.route('/<path:path>/_greeting/')
@parse_request_storage
def greeting(storage, path):
    return repr(storage) + '\n' + path
