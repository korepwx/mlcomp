# -*- coding: utf-8 -*-
import codecs
import json
import os
import socket
import stat
import time
from contextlib import contextmanager
from logging import getLogger

from mlcomp.persist.storage_meta import StorageMeta
from .errors import StorageReadOnlyError
from .utils import duplicate_console_output, BackgroundWorker

__all__ = ['Storage']

# Constants for storage classes
STORAGE_META_FILE = 'storage.json'
STORAGE_CONSOLE_LOG = 'console.log'
STORAGE_RUNNING_STATUS = 'running.json'
STORAGE_RUNNING_STATUS_INTERVAL = 2 * 60


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
        self.meta = StorageMeta(self, self.resolve_path(STORAGE_META_FILE))
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
