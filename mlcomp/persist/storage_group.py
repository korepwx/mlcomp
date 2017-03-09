# -*- coding: utf-8 -*-
import os
import random
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

    def __init__(self, path):
        path = os.path.abspath(path)
        self.path = path

    def resolve_path(self, *paths):
        """Join pieces of paths and make it absolute relative to group dir.

        Parameters
        ----------
        *paths : tuple[str]
            Path pieces relative to the work_dir of this group.

        Returns
        -------
        str
            Resolved absolute path.
        """
        return os.path.abspath(os.path.join(self.path, *paths))

    def iter_storage(self):
        """Iterate the storage directory under the group directory.

        Yield
        -----
        str
            The directory name of the storage.
        """
        for f in os.listdir(self.path):
            f_path = os.path.join(self.path, f)
            meta_file = os.path.join(f_path, STORAGE_META_FILE)
            if os.path.isfile(meta_file):
                yield f

    def list_storage(self):
        return list(self.iter_storage())

    @contextmanager
    def _lock_name(self, name, timeout=-1):
        """Lock the specified directory name."""
        with FileLock(self.resolve_path(name + '.lock'), timeout=timeout):
            yield

    def create_storage(self, basename=None, use_hostname=True,
                       datefmt='%Y%m%d.%H%M%S.%f'):
        """Create a new storage with unique name.

        If the `basename` is specified, the storage directory will
        have the name '{basename}_{hostname}_{datetime}`.  Otherwise
        it will have the name '{hostname}_{datetime}'.

        Parameters
        ----------
        basename : str
            Specify a basename for the storage.

        use_hostname : bool
            Whether or not to use hostname in the storage name?

        datefmt : str
            Specify the format for the datetime component in the name.

        Returns
        -------
        Storage
            The storage object, open in 'create' mode.
        """
        # gather the identity pieces of the storage name
        pieces = []
        if basename:
            pieces.append(basename)
        if use_hostname:
            try:
                pieces.append(socket.gethostname())
            except Exception:
                pass

        # search for a non-conflict directory name
        trial = 0
        pieces.append('')
        while True:
            # find a candidate name for the storage.
            pieces[-1] = datetime.now().strftime(datefmt)
            name = '_'.join(pieces)

            try:
                with self._lock_name(name, timeout=1):
                    path = self.resolve_path(name)
                    if not os.path.exists(path):
                        return Storage(path, 'create')
            except (LockTimeout, IOError):
                if trial >= 3:
                    raise

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
