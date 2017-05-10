# -*- coding: utf-8 -*-
import mimetypes
import os

from flask import send_from_directory
from werkzeug.exceptions import NotFound


def is_testing():
    """Whether or not the testing routes should be added?"""
    return os.environ.get('MLCOMP_TESTING') == '1'


def send_from_directory_ex(directory, filename, **kwargs):
    """Extended `send_from_directory`.

    This version of `send_from_directory` will would send 'abc.xxx.gz' as
    response to the request for 'abc.xxx'.
    """

    try:
        return send_from_directory(directory, filename, **kwargs)
    except NotFound:
        if 'mimetype' not in kwargs:
            # we should set the mime-type, otherwise Flask will
            # try to use the mime-type inferred from `filename + '.gz'`,
            # which is not controllable by us.
            mimetype = (
                mimetypes.guess_type(filename)[0] or
                'application/octet-stream'
            )
            kwargs['mimetype'] = mimetype
        ret = send_from_directory(directory, filename + '.gz', **kwargs)
        ret.headers['Content-Encoding'] = 'gzip'
        return ret