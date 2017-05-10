# -*- coding: utf-8 -*-
import gzip
import mimetypes
import os

import six

from mlcomp.utils import makedirs
from .base import ReportObject

__all__ = [
    'Resource', 'ResourceManager',
]


class Resource(ReportObject):
    """Resource object.

    Some reports might generate resources, for example, images for an
    Image report, or json data for a Figure report.

    Parameters
    ----------
    data
        Data of this resource.

    path : str
        Save path of this resource.

    extension : str
        Specify file extension of this resource.
        If not specified, will be inferred from `path` and `content_type`.

    content_type : str
        Content-type of this resource.

    gzip_compress : bool
        Whether or not to compress the data with gzip?

        If True, the data will be stored in `name_scope + extension + '.gz'`.
        Meanwhile, the stored path will still be `name_scope + extension`.
        (default is False)

    **kwargs
        Other arguments passed to `ReportObject`.
    """

    def __init__(self, data=None, path=None, extension=None, content_type=None,
                 gzip_compress=False, name=None, name_scope=None):
        super(Resource, self).__init__(name=name, name_scope=name_scope)
        if data is None and path is None:
            raise ValueError(
                'At least one of `data`, `path` should be specified.')
        if data and not isinstance(data, six.binary_type):
            raise TypeError('`data` must be binary type.')
        self._data = data
        self._extension = extension
        self._content_type = content_type
        self.path = path
        self.gzip_compress = gzip_compress

    def _repr_dict(self):
        ret = super(Resource, self)._repr_dict()
        ret.pop('data', None)
        return ret

    @property
    def has_loaded(self):
        return self._data is not None

    @property
    def has_saved(self):
        return self.path is not None

    @property
    def data(self):
        return self._data

    @property
    def extension(self):
        if self._extension is not None:
            return self._extension
        elif self.path is not None:
            return os.path.splitext(self.path)[1]
        elif self._content_type is not None:
            return mimetypes.guess_extension(self._content_type, strict=False)

    @property
    def content_type(self):
        if self._content_type is not None:
            return self._content_type
        elif self.path is not None:
            return mimetypes.guess_type(self.path)[0]
        elif self._extension is not None:
            return mimetypes.guess_type('0%s' % (self._extension,))[0]

    def to_config(self, sort_keys=False):
        ret = super(Resource, self).to_config(sort_keys=sort_keys)
        if not self.has_saved:
            ret['data'] = self._data
        if self._extension:
            ret['extension'] = self._extension
        if self._content_type:
            ret['content_type'] = self._content_type
        if not ret['gzip_compress']:
            ret.pop('gzip_compress')
        return ret

    def to_json(self, **kwargs):
        if not self.has_saved:
            raise RuntimeError('%r has not been saved' % (self,))
        return super(Resource, self).to_json(**kwargs)

    def save_resources(self, rm):
        if not self.has_loaded:
            raise RuntimeError('`data` has not been loaded.')
        if not rm.has_saved(self.name_scope):
            self.path = rm.save(
                data=self._data,
                name_scope=self.name_scope,
                extension=self.extension,
                gzip_compress=self.gzip_compress,
            )

    def load_resources(self, rm):
        if not self.has_loaded and self.has_saved:
            self._data = rm.load(
                path=self.path,
                gzip_compress=self.gzip_compress
            )


class ResourceManager(object):
    """Resources saver and loader.

    Parameters
    ----------
    save_dir : str
        The directory where to save the resources.

    rel_path : str
        The relative path of `save_dir`, when the resources are included
        in a report file.  Default is '', which suggests the file should
        be placed just at the root of `save_dir`.
    """

    def __init__(self, save_dir, rel_path=''):
        rel_path = rel_path.rstrip('/')
        if rel_path:
            rel_path += '/'
        self.save_dir = os.path.abspath(save_dir)
        self.rel_path = rel_path
        self._saved = {}

    def __repr__(self):
        return 'ResourceManager(%r)' % (self.save_dir,)

    def clear_saved(self):
        """Clear the dict of saved resources."""
        self._saved.clear()

    def has_saved(self, name_scope):
        """Check whether or not the resource at `name_scope` has been saved.

        Parameters
        ----------
        name_scope : str
            The name scope of the resource.
        """
        return name_scope in self._saved

    def save(self, data, name_scope, extension, gzip_compress=False):
        """Save `data` at specified `name_scope`.

        Parameters
        ----------
        data : bytes
            Binary data to be saved.

        name_scope : str
            The name scope of the resource.

        extension : str
            Optional extension for the save path.

        gzip_compress : bool
            Whether or not to store the data in gzip compressed file?
            (default is False)

        Returns
        -------
        str
            The save path.
        """
        if not isinstance(data, six.binary_type):
            raise TypeError(
                'at %r: `data` must be binary object.' %
                (name_scope,)
            )
        path = name_scope.strip('/')
        if not path:
            raise ValueError('`name_scope` must not be empty.')
        if extension:
            path += extension

        file_path = os.path.join(self.save_dir, path)
        parent_dir = os.path.split(file_path)[0]
        makedirs(parent_dir, exist_ok=True)

        if gzip_compress:
            with gzip.open(file_path + '.gz', 'wb') as f:
                f.write(data)
        else:
            with open(file_path, 'wb') as f:
                f.write(data)

        self._saved[name_scope] = self.rel_path + path
        return self._saved[name_scope]

    def load(self, path, gzip_compress=False):
        """Load data at specified save `path`.

        Parameters
        ----------
        path : str
            The save path, which is expected to start with `rel_path`.

        gzip_compress : bool
            Whether or not to load data from gzip compressed file?
            (default is False)

        Raises
        ------
        IOError
            If the path cannot be found, or cannot be loaded.

        ValueError
            If `path` does not start with `rel_path`.

        Returns
        -------
        bytes
            The loaded binary data.
        """
        if self.rel_path and not path.startswith(self.rel_path):
            raise ValueError(
                '%r does not start with %r.' % (path, self.rel_path))
        path = path[len(self.rel_path):].strip('/')
        path = os.path.join(self.save_dir, path)

        if gzip_compress:
            with gzip.open(path + '.gz', 'rb') as f:
                return f.read()
        else:
            with open(path, 'rb') as f:
                return f.read()
