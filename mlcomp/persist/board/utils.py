# -*- coding: utf-8 -*-
__all__ = ['MountTree']


class MountTreeNode(object):
    """Node for MountTree, each represent a node on the mount path.

    Parameters
    ----------
    name : str
        Name of this node in the parent.

    parent : MountTreeNode
        Parent of this node.

    data : any
        Data at this node.

    children : dict[str, MountTreeNode]
        Children of this node.
    """

    def __init__(self, name=None, parent=None, data=None, children=None):
        self.name = name
        self.parent = parent
        self.data = data
        self.children = children

    def __repr__(self):
        return repr(list(self.iter_mount_points()))

    @property
    def path(self):
        """Get the full path of this node.

        The returned path is ensured to end with "/", but not start with "/".
        """
        if self.parent is None:
            # root node should correspond to empty path
            return ''
        node = self
        ret = []
        while node.parent:
            ret.append(node.name)
            node = node.parent
        return '/'.join(reversed(ret)) + '/'

    def iter_mount_points(self):
        """Iterate through all the mount points.

        Yields
        ------
        (str, any)
            (path, data) at each mount point.

            `path` is ensured to end with "/".  Besides, descendants
            are ensured to be discovered earlier than ascendants.
        """
        stack = [(self.path, self, False)]
        while stack:
            path, node, expanded = stack.pop()
            if not expanded:
                if node.data:
                    stack.append((path, node, True))
                if node.children:
                    for name in sorted(node.children, reverse=True):
                        child = node.children[name]
                        stack.append((path + name + '/', child, False))
            else:
                yield (path, node.data)


class MountTree(object):
    """File-system like mount tree for indexing objects."""

    def __init__(self):
        self.root = MountTreeNode()

    def __repr__(self):
        return repr(list(self.iter_mount_points()))

    def get_node(self, path, expand=False, use_parent=False):
        """Get the node for specified path.

        Parameters
        ----------
        path : str
            The path of the node.

        expand : bool
            Whether or not to expand a parent node if the required
            child on the path does not exist?

        use_parent : bool
            Whether or not to return the parent node if expand
            is set to False, and the required child does not exist?

        Returns
        -------
        MountTreeNode | None
            The node, a parent node, or None.
        """
        node = self.root
        for p in (v for v in path.split('/') if v):
            if node.children is None:
                if expand:
                    node.children = {}
                else:
                    if not use_parent:
                        node = None
                    break
            if p not in node.children:
                if expand:
                    node.children[p] = MountTreeNode(p, node)
                else:
                    if not use_parent:
                        node = None
                    break
            node = node.children[p]
        return node

    def mount(self, path, data):
        """Mount data at specified path.

        Parameters
        ----------
        path : str
            The path where the data should be mounted.

            Segments should be separated by "/", and the empty segments
            will be ignored.

        data : any
            The data to be mounted at the path.

            If there's already data mounted at the path, it will be
            replaced by this one.
            Mount a None at specified path is equivalent to umount
            the specified path.
        """
        if data is None:
            self.unmount(path)
        else:
            self.get_node(path, expand=True).data = data

    def unmount(self, path):
        """Unmount data at specified path.

        Parameters
        ----------
        path : str
            The path where the data should be unmounted.

            No error will be raised if the path does not exist.
            If the path does not have any descendants, it will be
            removed from the tree.
        """
        node = self.get_node(path)
        if node:
            node.data = None
            while node.parent:
                if node.data is not None or node.children:
                    break
                node.parent.children.pop(node.name, None)
                node = node.parent

    def get(self, path, use_parent=False, closest_parent_only=False):
        """Get the data mounted at path or its parent path.

        Parameters
        ----------
        path : str
            The path to be get.

        use_parent : bool
            Whether or not to use mounted data from parent nodes if a
            required child on the path does not exist?

        closest_parent_only : bool
            If the parent node of a non-exist child still does not have
            data, whether or not to stay at this node (so that None will
            be returned) or try to get data from even the parent of parent?

            When True is specified, stay at the closest parent.
        """
        node = self.get_node(path, use_parent=use_parent)
        if node and use_parent and not closest_parent_only:
            # use_parent is True, at least we can get the root node
            assert(node is not None)
            while node.data is None and node.parent:
                node = node.parent
        if node:
            return node.data

    def iter_mount_points(self):
        """Iterate through all the mount points.

        Yields
        ------
        (str, any)
            (path, data) at each mount point.

            `path` is ensured to end with "/".  Besides, descendants
            are ensured to be discovered earlier than ascendants.
        """
        return self.root.iter_mount_points()
