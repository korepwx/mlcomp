# -*- coding: utf-8 -*-
from flask import Blueprint

from .utils import is_testing

main_bp = Blueprint('main', __name__.rsplit('.')[1])


if is_testing():
    @main_bp.route('/_hello/')
    def main_hello():
        """For testing purpose."""
        return 'main hello'
