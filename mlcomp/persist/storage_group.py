# -*- coding: utf-8 -*-
import os
import random
import re
import shutil
import socket
import time
from contextlib import contextmanager
from datetime import datetime

from filelock import FileLock, Timeout as LockTimeout

from .storage import STORAGE_META_FILE, Storage

__all__ = ['StorageGroup']


class StorageGroup(object):
    """Group of experiment storage directories.

    A storage group is a loose collection of experiment storage under
    the same parent directory.  Such directory structure is not required,
    but might be a most natural way to store the different trials of
    one experiment (of the same script).

    Parameters
    ----------
    path : str
        Path of the group directory.
    """

    DOUBLE_DELIM_REPLACER = re.compile('_{2,}')
    WELL_NAMED_PATTERN = re.compile('^(?:(.+)__)?(.+)__(\d{8}\.\d{6}\.\d{3})$')

    def __init__(self, path):
        path = os.path.abspath(path)
        self.path = path

    def resolve_path(self, *paths):
        """Join pieces of paths and make it absolute relative to group dir.

        Parameters
        ----------
        *paths : tuple[str]
            Path pieces relative to the path of this group.

        Returns
        -------
        str
            Resolved absolute path.
        """
        return os.path.abspath(os.path.join(self.path, *paths))

    def iter_storage(self, hostname=None, well_named=True):
        """Iterate the storage directory under the group directory.

        Parameters
        ----------
        hostname : str
            Include storage only if the hostname matches.
            This argument will imply `well_named`.

        well_named : bool
            Whether or not to include storage only if it is well-named?
            By 'well-named' it means that the storage should have the
            name '{basename}__{hostname}__{datetime}' or
            '{hostname}__{datetime}'.

        Yields
        ------
        str
            The directory name of the storage.
        """
        if hostname:
            hostname = self.DOUBLE_DELIM_REPLACER.sub('_', hostname)
            well_named = True

        for f in os.listdir(self.path):
            f_path = os.path.join(self.path, f)
            meta_file = os.path.join(f_path, STORAGE_META_FILE)
            if os.path.isfile(meta_file):
                if well_named:
                    m = self.WELL_NAMED_PATTERN.match(f)
                    if m:
                        if not hostname or hostname == m.group(2):
                            yield f
                else:
                    yield f

    def list_storage(self):
        return list(self.iter_storage())

    def open_latest_storage(self, hostname=None, mode='read'):
        """Open the latest storage according to name.

        This method only matches the well-named storage directories.
        It extracts the creation time of the storage directory from name.

        Parameters
        ----------
        hostname : str
            If specified, find the latest storage with this hostname only.

        mode : {'read', 'write', 'create'}
            In which mode should this storage to be open?
            See the constructor of `Storage` for more details.

        Returns
        -------
        Storage | None
            The latest storage directory, or None if not found.
        """
        candidate = None
        candidate_dt = None
        for f in self.iter_storage(hostname=hostname, well_named=True):
            dt = f.rsplit('__', maxsplit=1)[-1]
            dt = datetime.strptime(dt, '%Y%m%d.%H%M%S.%f')
            if candidate_dt is None or dt > candidate_dt:
                candidate = f
                candidate_dt = dt
        if candidate:
            return Storage(self.resolve_path(candidate), mode=mode)

    @contextmanager
    def _lock_name(self, name, timeout=-1):
        """Lock the specified directory name."""
        with FileLock(self.resolve_path(name + '.lock'), timeout=timeout):
            yield

    def create_storage(self, basename=None, hostname=None):
        """Create a new storage with unique name.

        If the `basename` is specified, the storage directory will
        have the name '{basename}__{hostname}__{datetime}`.  Otherwise
        it will have the name '{hostname}__{datetime}'.

        Parameters
        ----------
        basename : str
            Specify a basename for the storage.

        hostname : str
            Specify a hostname, instead of using the system hostname.

        Returns
        -------
        Storage
            The storage object, open in 'create' mode.
        """
        # gather the identity pieces of the storage name
        pieces = []
        if basename:
            basename = self.DOUBLE_DELIM_REPLACER.sub('_', basename)
            pieces.append(basename)

        if not hostname:
            try:
                hostname = socket.gethostname()
            except Exception:
                hostname = 'unknown'
        hostname = self.DOUBLE_DELIM_REPLACER.sub('_', hostname)
        pieces.append(hostname)

        # search for a non-conflict directory name
        trial = 0
        pieces.append('')
        while True:
            # find a candidate name for the storage.
            dt = datetime.now()
            pieces[-1] = datetime.now().strftime('%Y%m%d.%H%M%S')
            pieces[-1] += '.' + ('%06d' % dt.microsecond)[:3]
            name = '__'.join(pieces)

            try:
                with self._lock_name(name, timeout=1):
                    path = self.resolve_path(name)
                    if not os.path.exists(path):
                        return Storage(path, 'create')
            except (LockTimeout, IOError):
                if trial >= 3:
                    raise

            if trial >= 3:
                raise IOError('Failed to pick up a unique name for storage.')

            # wait a random amount of time before next trial.
            trial += 1
            time.sleep(random.random() * 0.1 + 0.01)

    def remove_storage(self, name):
        """Remove a specified storage directory from the group.

        Parameters
        ----------
        name : str
            Name of the storage directory.  If the specified directory
            is not a storage, the method will raise IOError.
        """
        storage_dir = self.resolve_path(name)
        if not os.path.isfile(os.path.join(storage_dir, STORAGE_META_FILE)):
            raise IOError('%r is not a storage directory.' % storage_dir)
        shutil.rmtree(storage_dir)
