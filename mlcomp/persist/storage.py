# -*- coding: utf-8 -*-
import codecs
import copy
import gzip
import json
import os
import random
import shutil
import stat
import time
from contextlib import contextmanager
from logging import getLogger

import re
import six

from mlcomp.utils import (BackgroundWorker, PathExcludes, default_path_excludes,
                          makedirs, statpath)
from .errors import StorageReadOnlyError
from .storage_meta import StorageMeta
from .storage_status import StorageRunningStatus
from .utils import duplicate_console_output

if six.PY2:
    JsonDecodeError = ValueError
else:
    from json import JSONDecodeError

__all__ = [
    'Storage',
    'STORAGE_META_FILE', 'STORAGE_CONSOLE_LOG', 'STORAGE_RUNNING_STATUS',
    'STORAGE_RUNNING_STATUS_INTERVAL', 'STORAGE_REPORT_DIR',
    'STORAGE_SCRIPT_DIR',
]

# Constants for storage classes
STORAGE_META_FILE = 'storage.json'
STORAGE_CONSOLE_LOG = 'console.log'
STORAGE_RUNNING_STATUS = 'running.json'
STORAGE_RUNNING_STATUS_INTERVAL = 2 * 60
STORAGE_REPORT_DIR = 'report'
STORAGE_SCRIPT_DIR = 'script'


def storage_property(name):
    return property(
        lambda self: getattr(self._meta, name),
        lambda self, value: setattr(self._meta, name, value)
    )


def try_rmtree(path):
    """Remove file or directory at `path`."""
    try:
        path = os.path.abspath(path)
        st = statpath(path, follow_symlinks=False)
    except IOError:
        if os.path.exists(path):
            raise
    else:
        if stat.S_ISDIR(st.st_mode):
            shutil.rmtree(path)
        else:
            os.remove(path)


def copy_tree(src, dst, excludes):
    """Copy directory `src` to `dst`."""
    makedirs(dst, exist_ok=True)
    for fname in os.listdir(src):
        srcpath = os.path.join(src, fname)
        if excludes is not None and excludes.is_excluded(srcpath):
            continue
        dstpath = os.path.join(dst, fname)
        if os.path.isdir(srcpath):
            copy_tree(srcpath, dstpath, excludes)
        else:
            shutil.copy(srcpath, dstpath)


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
            st = statpath(path, follow_symlinks=True)
        except (IOError, OSError):
            # 'read' or 'write' mode: raise all errors including in-exist
            if mode in ('read', 'write'):
                raise
            # 'create' mode: raise error if the directory exists.
            makedirs(path, exist_ok=False)
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
            except IOError:
                if not os.path.exists(status_file):
                    return None
                raise

            try:
                values = json.loads(cnt)
            except JSONDecodeError:
                retry += 1
                delay = (
                    random.random() * (retry_delay_max - retry_delay_min) +
                    retry_delay_min
                )
                time.sleep(delay)
            else:
                return StorageRunningStatus(
                    pid=values.get('pid'),
                    hostname=values.get('hostname'),
                    start_time=values.get('start_time'),
                    active_time=values.get('active_time')
                )

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
            makedirs(os.path.split(path)[0], exist_ok=True)
        return path

    def reload(self):
        """Reload contents from the storage."""
        self._meta.reload()
        self._running_status = self._load_running_status()

    def reopen(self, mode):
        """Re-open the storage in alternative mode.

        Parameters
        ----------
        mode : {'read', 'write', 'create'}
            In which mode should this storage to be open?

        Returns
        -------
        Storage
            A new storage opened in specified mode.
        """
        return Storage(self._path, mode)

    def to_dict(self):
        """Get the information of this storage as a dict."""
        ret = copy.copy(self._meta.values)
        ret['name'] = self.name
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
            (default is 'utf-8').

        Returns
        -------
        bytes | str
            The log of the file, as string or bytes.
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

        This method will open all other contexts, including `capture_logging()`
        and `keep_running_status()`.
        """
        try:
            with self.capture_logging(), self.keep_running_status():
                try:
                    yield
                except Exception:
                    # print the exception, so that it would be captured
                    # by the logging file.
                    getLogger(__name__).exception(
                        'An error occurred within storage context.')
                    raise
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

    def list_reports(self):
        """List the report directories of this storage.

        Returns
        -------
        list[str]
            The report directories under "report/" of this storage.
        """
        from mlcomp.report import REPORT_JSON_FILE
        report_dir = self.resolve_path(STORAGE_REPORT_DIR)
        try:
            ret = []
            for fname in os.listdir(report_dir):
                fpath = os.path.join(report_dir, fname, REPORT_JSON_FILE)
                if os.path.isfile(fpath):
                    ret.append(fname)
            ret.sort()
            return ret
        except IOError:
            return []

    def save_report(self, report, dir_name='default', overwrite=False):
        """Save a report object into the storage.

        Parameters
        ----------
        report : mlcomp.report.ReportObject
            The report object to be saved.

        dir_name : str
            Directory name where to store this report object.

            The report file will be actually placed at `'report/' + dir_name`.
            Default value for this argument is 'default'.

        overwrite : bool
            Whether or not to overwrite existing files?  Default is False.
        """
        if not dir_name:
            raise ValueError('`dir_name` must be non-empty.')
        if '/' in dir_name or '\\' in dir_name:
            raise ValueError('`dir_name` must not contain "/" or "\\".')
        self.check_write()
        from mlcomp.report import ReportSaver
        s = ReportSaver(self.resolve_path(STORAGE_REPORT_DIR, dir_name),
                        overwrite=overwrite)
        s.save(report)

    _PROTECTED_FILES = re.compile(
        r'''
          # match the start position
          ^

          # the main file pattern
          (?:
            # match protected directories
            (report)(?:$|[/\\].*)

            # match protected files
          | (storage\.json|console\.log|running.json)$
          )
        ''',
        re.VERBOSE
    )

    def copy_file(self, src, dst, overwrite=False):
        """Copy `src` file as `dst`.

        Parameters
        ----------
        src : str
            The source file path.

        dst : str
            The destination file path.  It should be the relative path
            of the file.  The parent directory will be created
            automatically if not exist.

        overwrite : bool
            Whether or not to overwrite existing file or directory?
            (default False)
        """
        dst_path = self.ensure_parent_exists(dst)
        dst_relpath = os.path.relpath(dst_path, self.path)
        if self._PROTECTED_FILES.match(dst_relpath):
            raise IOError('%r is protected and cannot be overwritten.' % (dst,))

        self.check_write()
        if os.path.exists(dst_path):
            if overwrite:
                try_rmtree(dst_path)
            else:
                raise IOError('Destination %r exists.' % (dst,))
        shutil.copy(os.path.abspath(src), dst_path)

    def copy_dir(self, src, dst, excludes=default_path_excludes,
                 overwrite=False):
        """Copy `src` directory as `dst`.

        Parameters
        ----------
        src : str
            The source directory path.

        dst : str
            The destination directory path.  It should be the relative
            path of the file.  The parent directory will be created
            automatically if not exist.

        excludes : PathExcludes
            The path excludes rule.
            If `None` is specified, will not exclude any path.

        overwrite : bool
            Whether or not to overwrite existing file or directory?
            (default False)
        """
        dst_path = self.ensure_parent_exists(dst)
        dst_relpath = os.path.relpath(dst_path, self.path)
        if self._PROTECTED_FILES.match(dst_relpath):
            raise IOError('%r is protected and cannot be overwritten.' % (dst,))

        self.check_write()
        if os.path.exists(dst_path):
            if overwrite:
                try_rmtree(dst_path)
            else:
                raise IOError('Destination %r exists.' % (dst,))
        copy_tree(os.path.abspath(src), dst_path, excludes)

    def save_script(self, script_path, excludes=default_path_excludes):
        """Save the specified experiment script(s) to storage.

        Script file(s) will be stored to "script/" directory of this
        storage.  Existing files under "script/" will be removed.

        Parameters
        ----------
        script_path : str
            The path of the experiment scripts.

            If the specified path is a file, it will be copied to
            "script/" with the same name.  Otherwise if the path
            is a directory, all the contents of this directory will
            be copied to "script/".

        excludes : PathExcludes
            The path excludes rule.
            If `None` is specified, will not exclude any path.
        """
        script_path = os.path.abspath(script_path)
        if os.path.isdir(script_path):
            self.copy_dir(script_path, STORAGE_SCRIPT_DIR, overwrite=True,
                          excludes=excludes)
        else:
            self.copy_file(
                script_path,
                os.path.join(STORAGE_SCRIPT_DIR, os.path.split(script_path)[1]),
                overwrite=True
            )

    def open_gzip(self, path, mode='rb', compresslevel=9,
                  encoding=None, errors=None, newline=None):
        """Open a gzip file for read or write.

        Parameters
        ----------
        path : str
            The path of gzip file, relative to the root of storage.

        mode, compresslevel, encoding, errors, newline
            Arguments passed to the gzip constructor.

        Returns
        -------
        gzip.GzipFile
            The opened gzip file.
        """
        return gzip.open(self.ensure_parent_exists(path), mode=mode,
                         compresslevel=compresslevel, encoding=encoding,
                         errors=errors, newline=newline)
