# -*- coding: utf-8 -*-
import six
from flask import Blueprint, jsonify, current_app

#: The blueprint of the main application
api_bp = Blueprint('api', __name__.rsplit('.')[1])


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
