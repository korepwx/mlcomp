# -*- coding: utf-8 -*-
import codecs
import copy
import json
import os
import random
import stat
import time
from contextlib import contextmanager
from json import JSONDecodeError
from logging import getLogger

from .errors import StorageReadOnlyError
from .storage_meta import StorageMeta
from .storage_status import StorageRunningStatus
from .utils import duplicate_console_output, BackgroundWorker

__all__ = ['Storage']

# Constants for storage classes
STORAGE_META_FILE = 'storage.json'
STORAGE_CONSOLE_LOG = 'console.log'
STORAGE_RUNNING_STATUS = 'running.json'
STORAGE_RUNNING_STATUS_INTERVAL = 2 * 60


def storage_property(name):
    return property(
        lambda self: getattr(self._meta, name),
        lambda self, value: setattr(self._meta, name, value)
    )


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

        self._name = os.path.split(path)[1]
        self._path = path
        self._mode = mode
        self._meta = StorageMeta(self, meta_file)
        self._running_status = self._load_running_status()
        self._logging_captured = False

    # the read-only properties of this class
    name = property(lambda self: self._name)
    path = property(lambda self: self._path)
    mode = property(lambda self: self._mode)
    running_status = property(lambda self: self._running_status)

    @property
    def is_active(self):
        """Whether or not this storage is active?"""
        running_status = self._running_status
        if running_status:
            now = time.time()
            diff = now - running_status.active_time
            if diff < STORAGE_RUNNING_STATUS_INTERVAL * 2:
                return True
        return False

    @property
    def update_or_active_time(self):
        """Get the last update or active time of this storage."""
        ret = None
        running_status = self._running_status
        if running_status:
            ret = running_status.active_time
        if not ret:
            ret = self._meta.update_time
        if not ret:
            ret = self._meta.create_time
        return ret

    # lift the meta properties as storage properties
    create_time = storage_property('create_time')
    has_error = storage_property('has_error')
    description = storage_property('description')
    tags = storage_property('tags')

    def __repr__(self):
        return 'Storage(%r)' % self._path

    def _load_running_status(self, retry_delay_min=0.01, retry_delay_max=0.1):
        retry = 0
        status_file = self.resolve_path(STORAGE_RUNNING_STATUS)
        while retry < 3:
            try:
                with codecs.open(status_file, 'rb', 'utf-8') as f:
                    cnt = f.read()
                values = json.loads(cnt)
                return StorageRunningStatus(
                    pid=values.get('pid'),
                    hostname=values.get('hostname'),
                    start_time=values.get('start_time'),
                    active_time=values.get('active_time')
                )
            except JSONDecodeError:
                retry += 1
                delay = (
                    random.random() * (retry_delay_max - retry_delay_min) +
                    retry_delay_min
                )
                time.sleep(delay)
            except IOError:
                if not os.path.exists(status_file):
                    return None
                raise

    @property
    def readonly(self):
        """Whether or not the storage is read-only?"""
        return self._mode == 'read'

    def check_write(self):
        """Raises StorageReadOnlyError if the storage is read-only."""
        if self.readonly:
            raise StorageReadOnlyError(self._path, 'storage is read-only')

    def resolve_path(self, *paths):
        """Join pieces of paths and make it absolute relative to storage dir.

        Parameters
        ----------
        *paths : str
            Path pieces relative to the work_dir of this storage.

        Returns
        -------
        str
            Resolved absolute path.
        """
        return os.path.abspath(os.path.join(self._path, *paths))

    def ensure_parent_exists(self, *paths):
        """Resolve the path pieces and ensure its parent exists."""
        path = self.resolve_path(*paths)
        if not os.path.isdir(path):
            self.check_write()
            os.makedirs(os.path.split(path)[0], exist_ok=True)
        return path

    def reload(self):
        """Reload contents from the storage."""
        self._meta.reload()
        self._running_status = self._load_running_status()

    def reopen(self, mode):
        """Re-open the storage in alternative mode."""
        return Storage(self._path, mode)

    def to_dict(self):
        """Get the information of this storage as a dict."""
        ret = copy.copy(self._meta.values)
        if self._running_status:
            ret['running_status'] = self._running_status.to_dict()
        ret['is_active'] = self.is_active
        ret['update_time'] = self.update_or_active_time
        return ret

    @contextmanager
    def capture_logging(self, filename=STORAGE_CONSOLE_LOG, append=True):
        """Capture the console output and logs within a context.

        Parameters
        ----------
        filename : str
            The target file where the captured contents should be saved to.
            Default is `STORAGE_CONSOLE_LOG`.

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
    def keep_running_status(self,
                            update_interval=STORAGE_RUNNING_STATUS_INTERVAL):
        """Keep updating the running status file within a context.

        Parameters
        ----------
        update_interval : float
            Number of seconds between two update of the status file.
        """

        self.check_write()
        filepath = self.ensure_parent_exists(STORAGE_RUNNING_STATUS)
        status = StorageRunningStatus.generate()
        self._running_status = status

        def update_status():
            status.active_time = time.time()
            status.save_file(filepath)
            # if one has called `reload()` during the keep status context,
            # the object will lose track of the latest status.
            # thus we need to set the status here.
            self._running_status = status

        worker = BackgroundWorker(update_status, update_interval)
        try:
            update_status()
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
            self._running_status = None

    @contextmanager
    def with_context(self):
        """Open a context that keeps this storage active.

        This method will open all other contexts, e.g., `capture_logging()`
        and `keep_running_status()`.  Furthermore, when existing the context
        of this method,
        """
        try:
            with self.capture_logging(), self.keep_running_status():
                yield
            self._meta.has_error = False
        except Exception:
            self._meta.has_error = True
            raise
        finally:
            try:
                self._meta.update_time = time.time()
            except Exception:
                getLogger(__name__).info(
                    'Failed to write update time of %r.', self, exc_info=True)

    def save_report(self, report, path='default', overwrite=False):
        """Save a report object into the storage.

        Parameters
        ----------
        report : mlcomp.report.ReportObject
            The report object to be saved.

        path : str
            Where to store the report object.

            The report file will be actually placed at `'report/' + path`.
            Default value for this argument is 'default'.

        overwrite : bool
            Whether or not to overwrite existing files?  Default is False.
        """
        if not path:
            raise ValueError('`path` must be non-empty.')
        from mlcomp.report import ReportSaver
        s = ReportSaver(self.resolve_path('report', path), overwrite=overwrite)
        s.save(report)
