# -*- coding: utf-8 -*-
import os
import re
from logging import getLogger

import six
from sortedcontainers import SortedDict
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .storage import Storage, STORAGE_META_FILE

__all__ = ['StorageTree', 'StorageTreeWatcher']


class StorageTreeNode(object):
    """Node of the storage tree.

    Each node on the storage tree should correspond to either
    an intermediate directory, or a storage directory.

    Parameters
    ----------
    name : str
        Name of the storage node.

    path : str
        Path of the storage directory.

    mode : {'read', 'write'}
        In which mode should the storage to be open?

    children : SortedDict[str, StorageTreeNode]
        The children nodes of this node.

    storage : Storage
        The storage object of this node.

    need_reload : bool
        Whether or not this node needs reloading?
    """

    IGNORE_PATTERNS = re.compile(
        r'''
          # match the start position, or parent directories
          (?:^|.*[/\\])

          # the main file pattern
          (?:
            # match the git or svn directory
            (\.git|\.svn)(?:$|.*[/\\])

            # match the DS_Store file.
          | (\.DS_Store)$
          )
        ''',
        re.VERBOSE
    )

    def __init__(self, name, path, mode, children=None, storage=None,
                 need_reload=False):
        if mode not in ('read', 'write'):
            raise ValueError('Invalid mode %r.' % mode)
        self.name = name
        self.path = os.path.abspath(path)
        self.mode = mode
        self._children = children   # type: SortedDict[str, StorageTreeNode]
        self._storage = storage     # type: Storage
        self._need_reload = need_reload

    def __repr__(self):
        return 'StorageTreeNode(%r)' % (self.path,)

    @classmethod
    def from_dir(cls, root_dir, mode):
        """Create the node from specified path."""
        def scan_dir(name, path):
            if not cls.IGNORE_PATTERNS.match(path):
                meta_file = os.path.join(path, STORAGE_META_FILE)
                if os.path.isfile(meta_file):
                    s = Storage(path, mode)
                    return StorageTreeNode(s.name, path, mode, storage=s)
                elif os.path.isdir(path):
                    children = []
                    for f in sorted(os.listdir(path)):
                        f_path = os.path.join(path, f)
                        node = scan_dir(f, f_path)
                        if node:
                            children.append((f, node))
                    if children:
                        children = SortedDict(children)
                        ret = StorageTreeNode(
                            name, path, mode, children=children)
                        return ret
        return scan_dir('', os.path.abspath(root_dir))

    def _reload(self):
        nd = self.from_dir(self.path, self.mode)
        if nd:
            self._children = nd.children
            self._storage = nd.storage
        else:
            self._children = self._storage = None
        self._need_reload = False

    def reload(self):
        """Force reloading the node."""
        self._reload()

    def set_reload(self):
        """Set the node to be reload later."""
        self._need_reload = True

    @property
    def need_reload(self):
        return self._need_reload

    @property
    def children(self):
        if self._need_reload:
            self._reload()
        return self._children

    @property
    def storage(self):
        if self._need_reload:
            self._reload()
        return self._storage


class StorageTree(object):
    """Tree of the storage directories on disk.

    Parameters
    ----------
    path : str
        The root directory of the storage tree.

    mode : {'read', 'write'}
        In which mode should the storage to be open?
    """

    def __init__(self, path, mode='read'):
        self.root = StorageTreeNode.from_dir(path, mode=mode)
        # if the path does not exist, the root might be None
        # in this case we need to construct an empty root
        if self.root is None:
            self.root = StorageTreeNode('', os.path.abspath(path), mode)

    def iter_storage(self):
        """Iterate through all the storage in this tree."""
        stack = [(False, self.root)]
        names = []
        while stack:
            expanded, node = stack.pop()
            if expanded:
                names.pop()
            else:
                names.append(node.name)
                storage, children = node.storage, node.children
                if storage:
                    yield '/'.join(names[1:]), storage
                    names.pop()
                elif children:
                    stack.append((True, node))
                    for c in reversed(list(six.itervalues(children))):
                        stack.append((False, c))

    def find_storage(self, path):
        """Find a storage according to the path.

        Parameters
        ----------
        path : str
            The path of the storage.

        Returns
        -------
        Storage
            The storage, or None if the storage does not exist.
        """
        names = re.split(r'[/\\]+', path)
        node = self.root
        for name in filter(lambda v: v, names):
            children = node.children
            if not children or name not in children:
                return None
            node = children[name]
        return node.storage

    def set_reload(self, path):
        """Set a given path to be reloaded later.

        Parameters
        ----------
        path : str
            The path to be reloaded.
        """
        names = re.split(r'[/\\]+', path)
        node = self.root
        for name in filter(lambda v: v, names):
            # we choose to use `_children` instead of `children`,
            # so as to set the reload flag of parent node,
            # instead of let the node to reload immediately.
            children = node._children
            if not children or name not in children:
                node.set_reload()
                return
            node = children[name]
        node.set_reload()


class StorageTreeFileEventHandler(FileSystemEventHandler):
    """File system event handler for a storage tree.

    Parameters
    ----------
    tree : StorageTree
        The storage tree.
    """

    def __init__(self, tree):
        self.tree = tree

    def get_relative_path(self, path):
        """Get the relative path according to tree root."""
        return os.path.relpath(path, self.tree.root.path)

    def path_event(self, path):
        """Handle the event regarding specified path."""
        try:
            # normalize the path and check whether or not it's in the tree
            rel_path = self.get_relative_path(path)
            path_pieces = [
                v for v in rel_path.split(os.sep)
                if v not in ('', '.')
            ]
            if not path_pieces or path_pieces == '..':
                return
            path = '/'.join(path_pieces)

            # set the specified tree node to be reloaded later
            self.tree.set_reload(path)
            getLogger(__name__).info(
                'File monitor: %r will be reloaded.' % path)
        except Exception:
            getLogger(__name__).info('File monitor error.', exc_info=True)

    def on_moved(self, event):
        super(StorageTreeFileEventHandler, self).on_moved(event)
        getLogger(__name__).debug(
            "FS event: moved: %r -> %r", event.src_path, event.dest_path)

        # for a move event, we need to set their parents to be reloaded
        self.path_event(os.path.split(event.src_path)[0])
        self.path_event(os.path.split(event.dest_path)[0])

    def on_created(self, event):
        super(StorageTreeFileEventHandler, self).on_created(event)
        getLogger(__name__).debug("FS event: created %r", event.src_path)

        # for a create event, we need to set the parent to be reloaded.
        self.path_event(os.path.split(event.src_path)[0])

    def on_deleted(self, event):
        super(StorageTreeFileEventHandler, self).on_deleted(event)
        getLogger(__name__).debug("FS event: removed %r", event.src_path)

        # for a remove event, we need to set the parent to be reloaded.
        self.path_event(os.path.split(event.src_path)[0])

    def on_modified(self, event):
        super(StorageTreeFileEventHandler, self).on_modified(event)
        getLogger(__name__).debug("FS event: changed: %r", event.src_path)

        # for a modify event, we need to set the path to be reloaded.
        self.path_event(event.src_path)


class StorageTreeWatcher(object):
    """File system watcher for the storage tree.

    Parameters
    ----------
    trees : collections.Iterable[StorageTree]
        The storage tree instances.
    """

    def __init__(self, trees):
        self.trees = list(trees)
        self.observer = Observer()
        for t in self.trees:
            handler = StorageTreeFileEventHandler(t)
            self.observer.schedule(handler, t.root.path, recursive=True)

    def start(self):
        """Start the watcher."""
        self.observer.start()

    def stop(self):
        """Stop the watcher."""
        self.observer.stop()
