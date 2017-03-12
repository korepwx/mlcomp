# -*- coding: utf-8 -*-
from flask import Blueprint

#: Main application blueprint
main_bp = Blueprint('main', __name__.rsplit('.')[1])


@main_bp.route('/')
def index():
    return 'hello, world.'
