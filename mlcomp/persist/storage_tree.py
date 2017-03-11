# -*- coding: utf-8 -*-
import os

from .storage import Storage


class StorageTreeNode(object):
    """Node of the storage tree.

    Each node on the storage tree should correspond to either
    an intermediate directory, or a storage directory.

    Parameters
    ----------
    name : str
        Name of the directory.

    storage : Storage
        The storage object.
    """

    def __init__(self, name, storage=None):
        self.name = name
        self.children = None    # type: list[StorageTreeNode]
        self.storage = storage  # type: Storage

    def __repr__(self):
        pieces = [self.name]
        if self.storage:
            pieces.append(repr(self.storage))
        if self.children:
            pieces.append('children=%r' % (self.children,))
        return 'StorageTreeNode(%s)' % ','.join(pieces)


class StorageTree(object):
    """Tree of the storage directories on disk.

    Parameters
    ----------
    root_dir : str
        The root directory of the storage tree.
    """

    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.root = None        # type: StorageTreeNode
        self.reload()

    def reload(self):
        """Reload the whole storage tree.

        This method will cause a full scan on the root directory.
        It might be rather slow, so do not call it too frequently.
        """

