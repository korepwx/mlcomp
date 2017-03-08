# -*- coding: utf-8 -*-
import codecs
import copy
import json
import os
import socket
import stat
from contextlib import contextmanager

from logging import getLogger

import time

from .errors import StorageReadOnlyError
from .utils import duplicate_console_output, BackgroundWorker

__all__ = ['Storage']

# Constants for storage classes
STORAGE_META_FILE = 'storage.json'
STORAGE_CONSOLE_LOG = 'console.log'
STORAGE_RUNNING_STATUS = 'running.json'
STORAGE_RUNNING_STATUS_INTERVAL = 2 * 60


class StorageMetaTags(object):
    """Storage meta tags."""

    def __init__(self, meta):
        self._meta = meta

    @property
    def _tags_or_empty(self):
        return self._meta.values.get('tags') or ()

    def __len__(self):
        return len(self._tags_or_empty)

    def __contains__(self, item):
        return item in self._tags_or_empty

    def __iter__(self):
        return iter(self._tags_or_empty)

    def __getitem__(self, item):
        return self._tags_or_empty[item]

    def __setitem__(self, key, value):
        with self._meta.modify_context():
            if 'tags' not in self._meta.values:
                raise IndexError('List assignment out of index.')
            self._meta.values['tags'] = value

    def __repr__(self):
        return repr(self._meta.values.get('tags'))

    def append(self, item):
        with self._meta.modify_context():
            if 'tags' not in self._meta.values:
                self._meta.values['tags'] = [item]
            else:
                self._meta.values['tags'].append(item)

    def remove(self, item):
        if 'tags' not in self._meta.values or \
                item not in self._meta.values['tags']:
            raise ValueError('%r not in list' % (item,))
        with self._meta.modify_context():
            self._meta.values['tags'].remove(item)


class StorageMetaProperty(object):
    """Storage meta property."""

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __get__(self, instance, owner):
        if not instance:
            return self
        try:
            return self.getter(instance)
        except KeyError:
            return None

    def __set__(self, instance, value):
        if not instance:
            return self
        with instance.modify_context():
            self.setter(instance, value)

    @staticmethod
    def default_named_getter(name):
        return lambda self: self.values[name]

    @staticmethod
    def default_named_setter(name):
        def set_value(self, value):
            self.values[name] = value
        return set_value

    @staticmethod
    def read_only_setter(self, value):
        raise RuntimeError('Attribute is read-only.')

    @staticmethod
    def named(name, getter=None, setter=None, readonly=False):
        if not getter:
            getter = StorageMetaProperty.default_named_getter(name)
        if readonly:
            setter = StorageMetaProperty.read_only_setter
        elif not setter:
            setter = StorageMetaProperty.default_named_setter(name)
        return StorageMetaProperty(getter, setter)


class StorageMeta(object):
    """Storage meta information."""

    def __init__(self, storage):
        self.storage = storage
        self.values = {}
        self._tags = StorageMetaTags(self)
        self.reload()

    def __repr__(self):
        return repr(self.values)

    @contextmanager
    def modify_context(self):
        """Open a context to modify the meta information.

        The meta information will be saved to storage immediately
        after leaving this context, if no error is raised.
        """
        self.storage.check_write()
        old_values = copy.copy(self.values)
        try:
            yield
            serialized = json.dumps(self.values)
            filepath = self.storage.resolve_path(STORAGE_META_FILE)
            with codecs.open(filepath, 'wb', 'utf-8') as f:
                f.write(serialized)
        except Exception:
            self.values = old_values
            raise

    def reload(self):
        """Reload the meta information from storage."""
        filepath = self.storage.resolve_path(STORAGE_META_FILE)
        try:
            with codecs.open(filepath, 'rb', 'utf-8') as f:
                self.values = json.load(f)
        except IOError:
            if os.path.exists(filepath):
                raise

    # mappers from json attributes to properties
    create_time = StorageMetaProperty.named('create_time', readonly=True)
    description = StorageMetaProperty.named('description')
    tags = StorageMetaProperty.named('tags', lambda self: self._tags)  # type: StorageMetaTags


class Storage(object):
    """Storage for experiment persistent.

    Parameters
    ----------
    path : str
        Path of the storage directory.

    mode : {'read', 'write', 'create'}
        In which mode should this storage to be open?

        If the mode is set to 'read', then any method that will cause
        the content of the storage to be modified will raise a
        StorageReadOnlyError to be raised.

        If the mode is set to 'write', the storage directory is expected
        to exist beforehand.  This is contrary to 'create' mode, where
        the directory is expected to be not exist.
    """

    def __init__(self, path, mode='read'):
        # check the arguments
        if mode not in ('read', 'write', 'create'):
            raise ValueError('Unknown mode %r.' % mode)

        path = os.path.abspath(path)
        meta_file = os.path.join(path, STORAGE_META_FILE)
        try:
            st = os.stat(path, follow_symlinks=True)
        except IOError:
            # 'read' or 'write' mode: raise all errors including in-exist
            if mode in ('read', 'write'):
                raise
            # 'create' mode: raise error if the directory exists.
            os.makedirs(path, exist_ok=False)
            initial_cnt = json.dumps({
                'create_time': time.time()
            })
            with codecs.open(meta_file, 'wb', 'utf-8') as f:
                f.write(initial_cnt)
        else:
            # non-directory entry should cause an error
            if not stat.S_ISDIR(st.st_mode):
                raise IOError('%r exists but is not a directory.' % path)

            # 'create' mode: exist directory should cause an error
            if mode == 'create':
                raise IOError(
                    'Cannot create an existing storage directory %r.' % path)

            # check the existence of meta file
            if not os.path.exists(meta_file):
                raise IOError('%r is not a storage directory.' % path)

        self.name = os.path.split(path)[1]
        self.path = path
        self.mode = mode
        self.meta = StorageMeta(self)
        self._logging_captured = False

    @property
    def readonly(self):
        """Whether or not the storage is read-only?"""
        return self.mode == 'read'

    def check_write(self):
        """Raises StorageReadOnlyError if the storage is read-only."""
        if self.readonly:
            raise StorageReadOnlyError(self.path, 'storage is read-only')

    def resolve_path(self, *paths):
        """Join pieces of paths and make it absolute relative to storage dir.

        Parameters
        ----------
        *paths : tuple[str]
            Path pieces relative to the work_dir of this storage.

        Returns
        -------
        str
            Resolved absolute path.
        """
        return os.path.abspath(os.path.join(self.path, *paths))

    def ensure_parent_exists(self, *paths):
        """Resolve the path pieces and ensure its parent exists."""
        path = self.resolve_path(*paths)
        if not os.path.isdir(path):
            self.check_write()
            os.makedirs(os.path.split(path)[0], exist_ok=True)
        return path

    def reload(self):
        """Reload contents from the storage."""
        self.meta.reload()

    @contextmanager
    def capture_logging(self, filename=STORAGE_CONSOLE_LOG, append=True):
        """Capture the console output and logs within a context.

        Parameters
        ----------
        filename : str
            The target file where the captured contents should be saved to.
            Default is STORAGE_CONSOLE_LOG.

        append : bool
            Whether or not to append the captured content if the logging
            file already exists?
        """
        self.check_write()
        if self._logging_captured:
            raise RuntimeError('Logging already captured.')
        with duplicate_console_output(self.ensure_parent_exists(filename),
                                      append=append):
            try:
                yield
            finally:
                self._logging_captured = False

    def get_captured_logging(self, filename=STORAGE_CONSOLE_LOG,
                             encoding='utf-8'):
        """Get the captured logs from file.

        Parameters
        ----------
        filename : str
            The target file where the captured contents should be saved to.
            Default is STORAGE_CONSOLE_LOG.

        encoding : str
            If specified None, will return the logs as bytes.
            Otherwise will decode the logs in specified codec.
            Default is 'utf-8'.
        """
        if encoding:
            with codecs.open(self.resolve_path(filename), 'rb', encoding) as f:
                return f.read()
        else:
            with open(self.resolve_path(filename), 'rb') as f:
                return f.read()

    @contextmanager
    def keep_running_status(self, filename=STORAGE_RUNNING_STATUS,
                            update_interval=STORAGE_RUNNING_STATUS_INTERVAL):
        """Keep updating the running status file within a context.

        Parameters
        ----------
        filename : str
            The running status file.

        update_interval : float
            Number of seconds between two update of the status file.
        """

        self.check_write()
        filepath = self.ensure_parent_exists(filename)

        def write_status():
            try:
                hostname = socket.gethostname()
            except Exception:
                hostname = None
            status = {
                'pid': os.getpid(),
                'hostname': hostname,
                'active_time': time.time(),
            }
            cnt = json.dumps(status)
            with codecs.open(filepath, 'wb', 'utf-8') as f:
                f.write(cnt)

        worker = BackgroundWorker(write_status, update_interval)
        try:
            worker.start()
            yield
        finally:
            worker.stop()
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                getLogger(__name__).warning(
                    'failed to remove running status file %r.',
                    filepath, exc_info=True
                )

    def get_running_status(self, filename=STORAGE_RUNNING_STATUS):
        """Get the running status.

        Parameters
        ----------
        filename : str
            The running status file.

        Returns
        -------
        dict[str, any]
            The running status dict.
        """
        with codecs.open(self.resolve_path(filename), 'rb', 'utf-8') as f:
            return json.load(f)
