# -*- coding: utf-8 -*-
import codecs
import json
import os
from logging import getLogger

import six
from flask import Flask, url_for

__all__ = ['Webpack']


class Webpack(object):
    """Extension to Flask application that supports webpack.js.

    Parameters
    ----------
    app : Flask
        Flask application.
    """

    def __init__(self, app):
        self.app = app

        # if `dev/assets.json` exists, use the development version of assets
        # otherwise use the production version of assets
        self.manifest_file = None
        for f in ('dev/assets.json', 'prod/assets.json'):
            manifest_file = os.path.abspath(os.path.join(app.static_folder, f))
            if os.path.exists(manifest_file):
                getLogger(__name__).info('Loaded assets from %r.', f)
                self.manifest_file = manifest_file
                self.manifest_dir = f[: f.find('/') + 1]
                break

        if self.manifest_file is None:
            raise IOError('No assets file can be loaded.')

        self.assets = {}
        self.mtime = None
        self.init_app(app)

    def init_app(self, app):
        # load the assets for the first time
        self._load_assets()

        # reload assets before each request if in development mode.
        if app.config.get('DEBUG', False):
            app.before_request(self._load_assets)

        # inject Flask application
        if hasattr(app, 'add_template_global'):
            app.add_template_global(self.asset_url_for)
        else:
            # Flask < 0.10
            ctx = {
                'asset_url_for': self.asset_url_for
            }
            app.context_processor(lambda: ctx)

    def _load_assets(self, force=False):
        """Load the assets manifest file.

        Parameters
        ----------
        force : bool
            If False, will not load the assets file if modify time is not
            newer than `self.mtime`.  If True, will force reloading the
            assets file.
        """
        def gather(target, origin, prefix=''):
            for k, v in six.iteritems(origin):
                if isinstance(v, dict):
                    gather(target, v, prefix + k + '/')
                else:
                    target[prefix + k] = self.manifest_dir + v
            return target

        try:
            mtime = os.stat(self.manifest_file).st_mtime
            if force or self.mtime is None or mtime > self.mtime:
                with codecs.open(self.manifest_file, 'rb', 'utf-8') as f:
                    # load and flatten the assets dict
                    assets = gather({}, json.load(f))
                self.mtime = mtime
                self.assets = assets

        except IOError:
            raise RuntimeError(
                '`%r` is not a valid json file.' % (self.manifest_file,))

    def asset_url_for(self, name):
        """Lookup the asset url according to name.

        Parameters
        ----------
        name : str
            Name of the asset.

        Returns
        -------
        str
            Asset url or None if not found.
        """
        ret = self.assets.get(name, None)
        if ret:
            return url_for('.static', filename=ret)
