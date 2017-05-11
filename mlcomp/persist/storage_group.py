# -*- coding: utf-8 -*-
import os
import random
import re
import shutil
import time
from datetime import datetime

from filelock import FileLock, Timeout as LockTimeout

from mlcomp.utils import makedirs
from .storage import STORAGE_META_FILE, Storage

__all__ = ['StorageName', 'StorageGroup']


class StorageName(object):
    """Well-defined storage name.

    A well-defined storage name should be composed of three parts:
    base name (optional), date of creation (required), and host name
    (optional).  These components should be separated by '__', and
    each of these components should not contain the separator.

    Parameters
    ----------
    basename
        The base name of the storage.

    creation
        The creation time as string.

    hostname
        The host name of the storage.
    """
    DATE_FMT = '%Y%m%d.%H%M%S.%f'
    WELL_DEFINED_NAME = re.compile(
        r'''
            ^
            (?:((?:[^_]|_(?!_))+)__)?   # the basename
            (\d{8}\.\d{6}\.\d{3})       # the creation
            (?:__((?:[^_]|_(?!_))+))?   # the hostname
            $
        ''',
        re.VERBOSE
    )
    CONTINUOUS_SEPARATOR = re.compile(r'_+')

    def __init__(self, basename, creation=None, hostname=None):
        if creation:
            self._create_time = datetime.strptime(creation, self.DATE_FMT)
        else:
            self._create_time = None
        self._creation = creation
        self._basename = basename
        self._hostname = hostname

    create_time = property(lambda self: self._create_time)
    creation = property(lambda self: self._creation)
    basename = property(lambda self: self._basename)
    hostname = property(lambda self: self._hostname)

    @property
    def name_tuple(self):
        return self.basename, self.creation, self.hostname

    def __str__(self):
        return '__'.join(filter(lambda s: s, self.name_tuple))

    def __repr__(self):
        return 'Storage(basename=%r,creation=%r,hostname=%r)' % self.name_tuple

    def __eq__(self, other):
        if isinstance(other, StorageName):
            return other.name_tuple == self.name_tuple
        return False

    @classmethod
    def parse(cls, name):
        """Parse the storage directory name."""
        m = cls.WELL_DEFINED_NAME.match(name)
        if m:
            return StorageName(*m.groups())
        return StorageName(name)

    @classmethod
    def filter_name(cls, name):
        """Filter out continuous '_' in the name."""
        return cls.CONTINUOUS_SEPARATOR.sub('_', name)

    @classmethod
    def unparse(cls, create_time, basename=None, hostname=None):
        """Create a well-defined name.

        Continuous '_' in `basename` and `hostname` will be replaced by one.

        Parameters
        ----------
        create_time : datetime
            The create time.

        basename : str
            Optional basename.

        hostname : str
            Optional hostname.
        """
        creation = create_time.strftime(cls.DATE_FMT)[:-3]
        basename = cls.filter_name(basename) if basename else None
        hostname = cls.filter_name(hostname) if hostname else None
        return StorageName(basename, creation, hostname)

    @property
    def well_defined(self):
        """Whether or not this name is well-defined?"""
        return (
            self.creation is not None and
            (self.basename is None or '__' not in self.basename) and
            (self.hostname is None or '__' not in self.hostname)
        )


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
        *paths : str | StorageName
            Path pieces relative to the path of this group.

        Returns
        -------
        str
            Resolved absolute path.
        """
        return os.path.abspath(
            os.path.join(self.path, *(str(s) for s in paths)))

    def ensure_parent_exists(self, *paths):
        """Resolve the path pieces and ensure its parent exists."""
        path = self.resolve_path(*paths)
        if not os.path.isdir(path):
            makedirs(os.path.split(path)[0], exist_ok=True)
        return path

    def iter_storage(self, hostname=None, well_defined=True):
        """Iterate the storage directory under the group directory.

        Parameters
        ----------
        hostname : str
            Include storage only if the hostname matches.
            This argument will imply `well_defined`.

        well_defined : bool
            Include storage only if its name is well-defined.

        Yields
        ------
        StorageName
        """
        if hostname:
            hostname = StorageName.filter_name(hostname)
            well_defined = True

        for f in os.listdir(self.path):
            f_path = os.path.join(self.path, f)
            meta_file = os.path.join(f_path, STORAGE_META_FILE)
            if os.path.isfile(meta_file):
                name = StorageName.parse(f)
                if not well_defined:
                    yield name
                elif name.well_defined and \
                        (hostname is None or name.hostname == hostname):
                    yield name

    def open_latest_storage(self, hostname=None, mode='read'):
        """Open the latest storage.

        This method only matches the well-named storage directories.
        It extracts the creation time of the storage directory from name.

        Parameters
        ----------
        hostname : str
            If specified, find the latest storage with this hostname.

        mode : {'read', 'write', 'create'}
            In which mode should this storage to be open?
            See the constructor of `Storage` for more details.

        Returns
        -------
        Storage | None
            The latest storage directory, or None if not found.
        """
        candidate = None
        for name in self.iter_storage(hostname=hostname, well_defined=True):
            if candidate is None or name.create_time > candidate.create_time:
                candidate = name
        if candidate:
            return Storage(self.resolve_path(candidate), mode=mode)

    def open_storage(self, name, mode='read'):
        """Open the storage according to name.

        Parameters
        ----------
        name : str
            Name of the storage directory.  If the specified directory
            is not a storage, the method will raise IOError.

        mode : {'read', 'write'}
            In which mode should this storage to be open?
            See the constructor of `Storage` for more details.
        """
        path = self.resolve_path(name)
        if not os.path.isfile(os.path.join(path, STORAGE_META_FILE)):
            raise IOError('%r is not a storage directory.' % path)
        return Storage(path, mode=mode)

    def create_storage(self, basename=None, hostname=None):
        """Create a new storage with unique name.

        Parameters
        ----------
        basename : str
            Specify a basename for the storage.

        hostname : str
            Specify a hostname for the storage (optional).

        Returns
        -------
        Storage
            The storage object, open in 'create' mode.
        """
        trial = 0
        while True:
            # find a non-conflict name for the storage.
            name = StorageName.unparse(datetime.now(), basename, hostname)
            try:
                path = self.ensure_parent_exists(name)
                with FileLock(path + '.lock', timeout=1):
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
        path = self.resolve_path(name)
        if not os.path.isfile(os.path.join(path, STORAGE_META_FILE)):
            raise IOError('%r is not a storage directory.' % path)
        shutil.rmtree(path)
