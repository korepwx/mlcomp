# -*- coding: utf-8 -*-
import os
import click
import six
from .application import MainApp

__all__ = ['main']

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_LEVEL = 'INFO'


@click.group()
def main():
    """ML Companion storage server."""


def init_logging(log_file, log_level, log_format):
    import logging.config
    config_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': log_format
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'formatter': 'default',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True
            },
            'tensorflow': {
                'handlers': ['default'],
                'level': 'WARN',
                'propagate': True
            },
        }
    }
    if log_file:
        config_dict['handlers']['logfile'] = {
            'level': log_level,
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.realpath(log_file),
            'maxBytes': 1048576
        }
        for logger in six.itervalues(config_dict['loggers']):
            logger['handlers'].append('logfile')
    logging.config.dictConfig(config_dict)


@click.command()
@click.option('-i', '--ip', default='', help='HTTP server IP.')
@click.option('-p', '--port', default=8080, help='HTTP server port.')
@click.option('-l', '--log-file', default=None, help='Save log to file.')
@click.option('-L', '--log-level', default=LOG_LEVEL, help='Log level.')
@click.option('-F', '--log-format', default=LOG_FORMAT, help='Log format.')
@click.option('-s', '--storage', multiple=True,
              help='Map a URL prefix to training storage. '
                   'For example, "-s /foo:/path/to/foo".')
@click.option('--debug', default=False, is_flag=True,
              help='Whether or not to enable debugging features?')
def run(ip, port, log_file, log_level, log_format, storage):
    """HTTP server for Madoka training storage browser."""
    # parse the storage mappings
    mappings = {}
    for s in storage:
        arr = s.split(':', 1)
        if len(arr) != 2:
            raise ValueError('%r: unrecognized mapping.' % (s,))
        prefix, path = tuple(arr)
        prefix = '/' + prefix.strip('/')
        path = os.path.realpath(path)
        mappings[prefix] = path
    # initialize the logging
    init_logging(log_file, log_level, log_format)
    # start the server
    server = MainApp(mappings)
    server.run(host=ip, port=port)
