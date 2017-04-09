# -*- coding: utf-8 -*-
from collections import OrderedDict

import six
from slugify import UniqueSlugify

from mlcomp.utils import camel_to_underscore, jsonutils
from .types import get_default_report_types

__all__ = [
    'ReportObject', 'ReportJsonEncoder', 'ReportJsonDecoder',
]


class ReportObject(object):
    """Base class for all report objects.

    A report object contains a piece of experiment results.  Such objects
    can be further composed up to form richer report objects.

    By default, a report object must only use public attributes for its
    serializable members.  Besides, all these serializable members should
    also be its construction arguments.  This behaviour could be override
    via `to_config` and `from_config` methods.

    Parameters
    ----------
    name : str
        Name of this report object.  If specified, it might be used as
        title in rendered page, and it would also be considered when
        determining the scope name of this report object.

    name_scope : str
        The name scope of this report object.  Name scope is the unique
        name that distinguishes every report object in a saved report
        file or rendered page.  It is serializable, however, will be
        regenerated each time a report object and its children are
        being saved onto disk, so as to ensure uniqueness.
    """

    def __init__(self, name=None, name_scope=None):
        self.name = name
        self.name_scope = name_scope

    def to_config(self, sort_keys=False):
        """Get the config values of this report object.

        Parameters
        ----------
        sort_keys : bool
            Whether or not to sort the keys?

        Returns
        -------
        dict[str, any]
            The dict of config values.  None values will be excluded
            from the returned dict.
        """
        key_values = [
            (k, v) for k, v in six.iteritems(self.__dict__)
            if not k.startswith('_') and v is not None
        ]
        if sort_keys:
            key_values.sort(key=lambda x: x[0])
            return OrderedDict(key_values)
        return dict(key_values)

    @classmethod
    def from_config(cls, config_dict):
        """Construct a report object from `config_dict`.

        Parameters
        ----------
        config_dict : dict[str, any]
            The dict of serializable member values.
        """
        return cls(**config_dict)

    def to_json(self, **kwargs):
        """Serialize the report object into JSON.

        Parameters
        ----------
        **kwargs
            Additional arguments passed to the JsonEncoder.
        """
        return ReportJsonEncoder(**kwargs).encode(self)

    @staticmethod
    def from_json(json, **kwargs):
        """Deserialize the report object from JSON.

        Parameters
        ----------
        json : str
            The serialized JSON source of the report object.

        **kwargs
            Additional arguments passed to the JsonDecoder.
        """
        return ReportJsonDecoder(**kwargs).decode(json)

    def gather_children(self):
        """Gather all the children directly belonging to this report object.

        The children gathered by this method should be in deterministic order,
        i.e., calling this method of identical report object should result in
        identical children list.

        Returns
        -------
        list[ReportObject]
            List of children, not guaranteed to be deduplicated.
        """
        ret = []
        for c in six.itervalues(self.to_config(sort_keys=True)):
            if isinstance(c, ReportObject):
                ret.append(c)
        return ret

    def assign_name_scopes(self):
        """Assign scope names to this object as well as all its descendants."""
        def get_slugify():
            def inner(report):
                candidate = report.name
                if candidate is None:
                    candidate = camel_to_underscore(report.__class__.__name__)
                return slugify(candidate)
            slugify = UniqueSlugify(to_lower=True, max_length=64, separator='_',
                                    stop_words=('a', 'an', 'the'))
            return inner

        # first, clear the existing scope names
        stack = [self]
        while stack:
            c = stack.pop()
            c.name_scope = None
            stack.extend(reversed(c.gather_children()))

        # next, generate the scope names of this report and its descendants
        stack = [(self, '', get_slugify())]
        while stack:
            r, path, r_slugify = stack.pop()
            if r.name_scope is None:
                # A report object may be added as children of more than one
                # report object.  Thus if a report object already has its
                # scope name at this point, it must be assigned by other
                # parent of this report object earlier.
                r.name_scope = path + r_slugify(r)
            c_slugify = get_slugify()
            for c in reversed(r.gather_children()):
                stack.append((c, r.name_scope + '/', c_slugify))

    def save_resources(self, rm):
        """Save the resources of this object as well as its descendants.

        The scope names must be assigned before this method is executed.
        Default behavior of this method is to call `save_resources` of
        all its direct children.

        Parameters
        ----------
        rm : mlcomp.report.ResourceManager
            The resource manager.
        """
        stack = list(reversed(self.gather_children()))
        while stack:
            c = stack.pop()
            c.save_resources(rm)
            stack.extend(reversed(c.gather_children()))

    def load_resources(self, rm):
        """Load the resources of this object as well as its descendants.

        The scope names must be assigned before this method is executed.
        Default behavior of this method is to call `load_resources` of
        all its direct children.

        Parameters
        ----------
        rm : mlcomp.report.ResourceManager
            The resource manager.
        """
        stack = list(reversed(self.gather_children()))
        while stack:
            c = stack.pop()
            c.load_resources(rm)
            stack.extend(reversed(c.gather_children()))

    def _repr_dict(self):
        return self.to_config(sort_keys=True)

    def __repr__(self):
        config_dict = self._repr_dict()
        pieces = ','.join(
            '%s=%s' % (k, repr(v))
            for k, v in six.iteritems(config_dict)
        )
        return '%s(%s)' % (self.__class__.__name__, pieces)


class ReportJsonEncoder(jsonutils.JsonEncoder):
    """Json encoder with support of report objects."""

    def _report_object_handler(self, o):
        if isinstance(o, ReportObject):
            report_types = get_default_report_types()
            report_type = report_types.type_to_name(o.__class__)
            config_dict = o.to_config()
            if '__type__' in config_dict or '__id__' in config_dict:
                raise ValueError(
                    '"__type__" and "__id__" are preserved keys and '
                    'cannot be used in config dict.'
                )
            config_dict['__type__'] = report_type
            yield config_dict

    OBJECT_HANDLERS = (
        jsonutils.JsonEncoder.OBJECT_HANDLERS + [_report_object_handler]
    )


class ReportJsonDecoder(jsonutils.JsonDecoder):
    """Json decoder with support of report objects."""

    def _report_object_handler(self, v):
        v_type = v['__type__']
        try:
            report_types = get_default_report_types()
            report_type = report_types.name_to_type(v_type)
        except (ImportError, KeyError, TypeError):
            pass
        else:
            v.pop('__type__')
            v.pop('__id__', None)
            yield report_type.from_config(v)

    OBJECT_HANDLERS = (
        jsonutils.JsonDecoder.OBJECT_HANDLERS + [_report_object_handler]
    )
