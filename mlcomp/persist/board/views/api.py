# -*- coding: utf-8 -*-
import six
from flask import Blueprint, jsonify, current_app

from .utils import is_testing

api_bp = Blueprint('api', __name__.rsplit('.')[1])


if is_testing():
    @api_bp.route('/_hello/')
    def api_hello():
        return jsonify('api hello')


@api_bp.route('/all')
def all_storage():
    """Get all storage in JSON."""
    trees = current_app.trees
    gathered = []
    for prefix, tree in six.iteritems(trees):
        gathered.extend(
            (prefix + '/' + path, storage.to_dict())
            for path, storage in tree.iter_storage()
        )
    gathered.sort(key=lambda v: v[0])
    return jsonify(gathered)
