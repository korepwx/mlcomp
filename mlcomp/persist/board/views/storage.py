# -*- coding: utf-8 -*-
from flask import Blueprint

#: The storage blueprint
storage_bp = Blueprint('storage', __name__.rsplit('.')[1])


@storage_bp.route('/_greeting/')
def greeting():
    return 'hello, world.'
