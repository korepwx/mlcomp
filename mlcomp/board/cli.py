# -*- coding: utf-8 -*-
import multiprocessing
import os

import click
import six

from mlcomp.board import config
from mlcomp.persist import STORAGE_META_FILE
from mlcomp.report import REPORT_JSON_FILE
from .application import BoardApp, StorageApp, ReportApp

try:
    from gunicorn.app.base import BaseApplication
except ImportError:
    BaseApplication = None

__all__ = ['main']

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_LEVEL = 'INFO'


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


def get_application_for_path(path):
    """Get the most proper application for specified `path`.
    
    If `path + '/storage.json'` exists, returns a `StorageApp`.
    If `path + '/report.json'` exists, returns a `ReportApp`.
    Otherwise returns a `BoardApp` with `path` mapped to root.
    
    Parameters
    ----------
    path : str
        The path to be served through web application.
        
    Returns
    -------
    (class, tuple, dict)
        The class, as well as the args and kwargs to construct the instance.
    """
    path = os.path.abspath(path)
    if os.path.exists(os.path.join(path, STORAGE_META_FILE)):
        return StorageApp, (path,), {}
    elif os.path.exists(os.path.join(path, REPORT_JSON_FILE)):
        return ReportApp, (path,), {}
    else:
        return BoardApp, ({'/': path},), {}


if BaseApplication:
    class GUnicornWrapper(BaseApplication):

        def __init__(self, app_factory, options=None):
            self.options = options or {}
            self.app_factory = app_factory
            super(GUnicornWrapper, self).__init__()

        def load_config(self):
            cfg = dict([
                (key, value)
                for key, value in six.iteritems(self.options)
                if key in self.cfg.settings and value is not None
            ])
            for key, value in six.iteritems(cfg):
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.app_factory()
else:
    GUnicornWrapper = None


@click.command()
@click.option('-h', '--host', default='',
              help='HTTP server host (IP:PORT). '
                   'Use 8080 as port if not specified.')
@click.option('-l', '--log-file', default=None, help='Save log to file.')
@click.option('-L', '--log-level', default=LOG_LEVEL, help='Log level.')
@click.option('-F', '--log-format', default=LOG_FORMAT, help='Log format.')
@click.option('-r', '--root', default=None,
              help='Root path to be served. Ignored if "-s" is specified. '
                   'Default is the current directory.')
@click.option('-p', '--prefix', multiple=True,
              help='Map a URL prefix to local path. '
                   'For example, "-p /foo:/path/to/foo".')
@click.option('-w', '--workers', default=None,
              help='Number of worker processes.')
@click.option('--debug', default=False, is_flag=True,
              help='Whether or not to enable debugging features?')
def main(host, log_file, log_level, log_format, root, prefix, workers, debug):
    """MLComp experiment browser."""
    # parse the host into ip & port
    ip = ''
    port = 8080
    if host:
        if ':' in host:
            ip, port = host.rstrip(':', 1)
            port = int(port)
        else:
            ip = host

    # set the debug flag if required
    if debug:
        config['DEBUG'] = True

    # if the prefix is not specified, get an application for specified `root`
    if not prefix:
        if not root:
            root = os.path.abspath(os.path.curdir)
        else:
            root = os.path.abspath(root)
        if not os.path.exists(root):
            raise IOError('%r does not exist.' % (root,))
        cls, args, kwargs = get_application_for_path(root)

    # otherwise compose a board app according to the mappings
    else:
        mappings = {}
        for pfx in prefix:
            arr = pfx.split(':', 1)
            if len(arr) != 2:
                raise ValueError('%r: unrecognized URL mapping.' % (pfx,))
            prefix, path = tuple(arr)
            prefix = '/' + prefix.strip('/')
            path = os.path.realpath(path)
            mappings[prefix] = path
        cls, args, kwargs = BoardApp, (mappings,), {}

    # initialize the logging
    init_logging(log_file, log_level, log_format)

    # start the server
    if debug or not issubclass(cls, BoardApp) or GUnicornWrapper is None:
        # since only `BoardApp` needs high-performance web server,
        # and since only `StorageApp` requires `with_context()`,
        # we just run the applications except `BoardApp` in single
        # threaded mode.
        app = cls(*args, **kwargs)
        with app.with_context():
            app.run(host=ip, port=port)
    else:
        if not workers:
            workers = (multiprocessing.cpu_count() * 2) + 1
        options = {
            'bind': '%s:%s' % (ip, port),
            'workers': workers,
        }
        GUnicornWrapper(lambda: cls(*args, **kwargs), options).run()
