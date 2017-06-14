# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import stat
import time
from logging import getLogger
from zipfile import ZIP_DEFLATED

import six
import zipstream
from flask import (Blueprint, current_app, send_from_directory, render_template,
                   jsonify, request, url_for, safe_join, Response)
from werkzeug.exceptions import NotFound, MethodNotAllowed, InternalServerError

from .utils import is_testing, send_from_directory_ex

if six.PY2:
    from urllib import quote as urlquote
else:
    from urllib.parse import quote as urlquote

storage_bp = Blueprint('storage', __name__.rsplit('.')[1])


def parse_request_storage(method):
    """Decorator that parses the request path to find the storage.

    The storage as well as the request path inside the storage will
    be passed to the method as named argument `storage` and `path`.
    """
    @six.wraps(method)
    def wrapped(*args, **kwargs):
        if current_app.is_board_app:
            # first, find the tree and get the path in the tree
            path = kwargs.pop('path', '')
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
            # now we've get the path inside tree, continue to get the storage
            tree = node.data
            storage_and_path = tree.find_storage(path)
            if not storage_and_path:
                raise NotFound()
            storage, storage_path = storage_and_path
            # get the path of the storage
            if pop_items:
                storage_path = '/'.join(pop_items) + '/' + storage_path
            storage_path = storage_path.strip('/')
            # and get the path inside the storage
            path = os.path.abspath(os.path.join(tree.path, path))
            path = os.path.relpath(path, storage.path).replace('\\', '/')
            path = '/'.join(v for v in path.split('/') if v not in ('', '.'))
            # finally, call the method
            kwargs.setdefault('storage', storage)
            kwargs.setdefault('root', storage_path)
            kwargs.setdefault('path', path)
            return method(*args, **kwargs)
        else:
            path = kwargs.pop('path', '')
            path = '/'.join(v for v in path.split('/') if v)
            kwargs.setdefault('storage', current_app.storage)
            kwargs.setdefault('root', '')
            kwargs.setdefault('path', path)
            return method(*args, **kwargs)
    return wrapped


if is_testing():
    @storage_bp.route('/_hello/')
    def storage_hello():
        return 'storage hello'


    @storage_bp.route('/_greeting/')
    @storage_bp.route('/<path:path>/_greeting/')
    @parse_request_storage
    def storage_greeting(storage, root, path):
        return '\n'.join([
            'storage greeting',
            storage.path,
            root,
            path
        ])


def handle_storage_index(storage, root_url, path):
    if request.method == 'GET':
        return render_template('storage.html', storage=storage,
                               root_url=json.dumps(root_url))
    else:
        raise MethodNotAllowed()


def handle_storage_info(storage, root_url, path):
    if request.method == 'POST':
        s_update = request.json
        s = storage.reopen('write')
        if 'description' in s_update:
            s.description = s_update['description'].strip()
        if 'tags' in s_update:
            s.tags = list(s_update['tags'])
        storage.reload()
    s_dict = storage.to_dict()
    s_dict['__type__'] = 'StorageInfo'
    s_dict['reports'] = storage.list_reports()
    s_dict['root_url'] = root_url
    return jsonify(s_dict)


def handle_file_stat(storage, root_url, path):
    def stat_to_entity(n, s):
        return {
            'name': n,
            'size': s.st_size,
            'is_dir': stat.S_ISDIR(s.st_mode)
        }

    fpath = safe_join(storage.path, path)
    try:
        st = os.stat(fpath)
    except OSError:
        if not os.path.exists(fpath):
            raise NotFound()
        getLogger(__name__).exception('Failed to stat %r.', fpath)
        raise InternalServerError()

    if stat.S_ISDIR(st.st_mode):
        ret = []
        for fname in os.listdir(fpath):
            try:
                f_stat = os.stat(os.path.join(fpath, fname))
                ret.append(stat_to_entity(fname, f_stat))
            except OSError:
                getLogger(__name__).exception('Failed to stat %r.', fpath)
        return jsonify(ret)
    else:
        return jsonify(stat_to_entity(os.path.split(fpath)[1], st))


def handle_storage_zip(storage):
    def collect(z, path, relpath):
        if os.path.isdir(path):
            for fname in os.listdir(path):
                f_path = os.path.join(path, fname)
                f_relpath = relpath + '/' + fname
                collect(z, f_path, f_relpath)
        else:
            z.write(path, arcname=relpath)

    def gen():
        z = zipstream.ZipFile(mode='w', compression=ZIP_DEFLATED)
        collect(z, os.path.abspath(storage.path), storage.name)
        for chunk in z:
            yield chunk

    response = Response(gen(), mimetype='application/zip')
    response.headers['Content-Disposition'] = (
        'attachment; filename=%s' % (urlquote(storage.name + '.zip'))
    )
    return response


def handle_storage_delete(storage):
    if request.method != 'POST':
        raise MethodNotAllowed()

    shutil.rmtree(storage.path)
    # wait for a sufficient time, so that the storage tree is ensured to be
    # reloaded.
    time.sleep(0.5)
    return jsonify({'error': 0})


@storage_bp.route('/', methods=['GET', 'POST'])
@storage_bp.route('/<path:path>', methods=['GET', 'POST'])
@parse_request_storage
def resources(storage, root, path):
    """Get resources from the storage directory."""
    root_url = url_for('.resources', path=root)
    if not root_url.endswith('/'):
        root_url += '/'

    # if the storage index page is requested
    if STORAGE_INDEX_URL.match(path):
        return handle_storage_index(storage, root_url, path)

    # if the storage info JSON is requested
    if path == 'info':
        return handle_storage_info(storage, root_url, path)

    # if the storage deletion is requested
    if path == 'delete':
        return handle_storage_delete(storage)

    # all of the remaining routes do not accept POST requests
    if request.method != 'GET':
        raise MethodNotAllowed()

    # if some static resources displayed at storage index are requested
    if path.startswith('report/') or path in ('console.log', 'storage.json'):
        return send_from_directory_ex(storage.path, path)

    # if the files are requested
    if path.startswith('files/') or path == 'files':
        if request.args.get('stat', None) == '1':
            return handle_file_stat(storage, root_url, path[6:])
        else:
            return send_from_directory(storage.path, path[6:])

    # if the storage zip archive is requested
    if path == 'archive.zip':
        return handle_storage_zip(storage)

    # no route is matched
    raise NotFound()

STORAGE_INDEX_URL = re.compile(
    r'^(/?|report(/[^/]+)?/?|browse(?:/.*)?|console/?)$'
)
