# -*- coding: utf-8 -*-
import os


def is_testing():
    """Whether or not the testing routes should be added?"""
    return os.environ.get('MLCOMP_TESTING') == '1'
