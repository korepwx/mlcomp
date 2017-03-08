# -*- coding: utf-8 -*-

__all__ = ['*']


class StorageError(Exception):
    """Base class for all storage errors.

    Parameters
    ----------
    storage_dir : str
        The path of the storage directory.
    """

    def __init__(self, storage_dir, *args):
        self.storage_dir = storage_dir
        super(Exception, self).__init__(storage_dir, *args)

    def __str__(self):
        fmt = ['%r']
        args = [self.storage_dir]    # type: list[any]
        if len(self.args) == 1:
            fmt.append('%s')
            args.append(self.args[1])
        elif len(self.args) > 2:
            fmt.append('%r')
            args.append(self.args[1:])
        return ': '.join(fmt) % tuple(args)


class StorageReadOnlyError(StorageError):
    """Error that is raised when writing to a read-only storage."""
