# -*- coding: utf-8 -*-
import codecs
import copy
import json
from contextlib import contextmanager

from sortedcontainers import SortedSet

__all__ = []


class StorageMetaTags(object):
    """Storage meta tags proxy."""

    def __init__(self, meta, tags=None):
        self.meta = meta
        self.items = SortedSet(tags or ())

    def __repr__(self):
        return 'Tags(%s)' % ','.join(repr(s) for s in self.items)

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def add(self, item):
        if item not in self.items:
            with self.meta.modify_context():
                self.items.add(item)

    def remove(self, item):
        if item in self.items:
            with self.meta.modify_context():
                self.items.remove(item)

    def set_items(self, items):
        self.items = SortedSet(items or ())


class StorageMetaProperty(object):
    """Storage meta property."""

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __get__(self, instance, owner):
        if not instance:
            return self
        try:
            return self.getter(instance)
        except KeyError:
            return None

    def __set__(self, instance, value):
        if not instance:
            return self
        with instance.modify_context():
            self.setter(instance, value)

    @staticmethod
    def default_named_getter(name):
        return lambda self: self.values[name]

    @staticmethod
    def default_named_setter(name):
        def set_value(self, value):
            self.values[name] = value
        return set_value

    @staticmethod
    def read_only_setter(self, value):
        raise RuntimeError('Attribute is read-only.')

    @staticmethod
    def named(name, getter=None, setter=None, readonly=False):
        if not getter:
            getter = StorageMetaProperty.default_named_getter(name)
        if readonly:
            setter = StorageMetaProperty.read_only_setter
        elif not setter:
            setter = StorageMetaProperty.default_named_setter(name)
        return StorageMetaProperty(getter, setter)


class StorageMeta(object):
    """Storage meta information."""

    def __init__(self, storage, meta_file):
        self.storage = storage
        self.meta_file = meta_file
        self.values = {}
        self._tags = None
        self.reload()

    def __repr__(self):
        return repr(self.values)

    @contextmanager
    def modify_context(self):
        """Open a context to modify the meta information.

        The meta information will be saved to storage immediately
        after leaving this context, if no error is raised.
        """
        self.storage.check_write()
        old_values = copy.copy(self.values)
        try:
            yield
            if self._tags:
                self.values['tags'] = list(self._tags)
            else:
                self.values.pop('tags', None)
            serialized = json.dumps(self.values)
            with codecs.open(self.meta_file, 'wb', 'utf-8') as f:
                f.write(serialized)
        except Exception:
            self.values = old_values
            raise

    def reload(self):
        """Reload the meta information from file."""
        with codecs.open(self.meta_file, 'rb', 'utf-8') as f:
            self.values = json.load(f)
            self._tags = StorageMetaTags(self, self.values.get('tags'))

    # mappers from json attributes to properties
    create_time = StorageMetaProperty.named('create_time', readonly=True)
    description = StorageMetaProperty.named('description')
    tags = StorageMetaProperty.named(
        'tags',
        lambda self: self._tags,
        lambda self, value: self._tags.set_items(value)
    )  # type: StorageMetaTags
