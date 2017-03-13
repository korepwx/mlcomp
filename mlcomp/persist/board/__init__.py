# -*- coding: utf-8 -*-
import os
import sys

from flask import Config


def __init_config():
    from . import defconfig
    config.from_object(defconfig)
    for config_file in ('/etc/mlcomp-board.conf',
                        os.path.expanduser('~/.mlcomp-board.conf')):
        if os.path.exists(config_file):
            config.from_pyfile(config_file)
    del sys.modules[__name__].__init_config

config = Config(os.path.abspath(os.path.curdir))
__init_config()
