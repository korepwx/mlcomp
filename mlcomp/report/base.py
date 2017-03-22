# -*- coding: utf-8 -*-
import six

from mlcomp.utils import (JsonConfigSerializer, JsonConfigObject,
                          AutoReprObject, camel_to_underscore)

__all__ = ['Report', 'register_report_type']


def register_report_type(report_type, type_name=None):
    """Register a report type to support serialization.

    Parameters
    ----------
    report_type : class
        The report class object.

    type_name : str
        Name of this type used in serialized JSON dict.
        If not specified, will use the class name of the type.

    Raises
    ------
    KeyError
        If `type_name` is duplicated.
    """
    if not isinstance(report_type, six.class_types) or \
            not issubclass(report_type, Report):
        raise TypeError(
            '`report_type` %r is not a Report class.' % (report_type,))
    if not type_name:
        type_name = report_type.__name__
    if type_name in __report_types__:
        raise KeyError('`type_name` %r is duplicated.' % (type_name,))
    __report_types__[type_name] = report_type
    __report_type_names__[report_type] = type_name

__report_types__ = {}
__report_type_names__ = {}


class ReportJsonSerializer(JsonConfigSerializer):
    """Extended JSON config object serializer for `Report`."""

    def to_json_value(self, o):
        if isinstance(o, Report):
            return o.to_config()
        return super(ReportJsonSerializer, self).to_json_value(o)

    def from_json_value(self, v, o_type):
        if issubclass(o_type, Report):
            return o_type.from_config(v)
        return super(ReportJsonSerializer, self).from_json_value(v, o_type)


class Report(JsonConfigObject, AutoReprObject):
    """Base class for all report objects.

    A report object contains a piece of experiment result.
    Such objects can be further combined to form a richer report.

    Parameters
    ----------
    title : str
        Title of this report.

    children : list[Report]
        Children of this report object.
    """

    __json_serializer__ = ReportJsonSerializer
    __json_attributes__ = {
        'title': str,
        'children': list
    }

    def __init__(self, title=None, children=None):
        self.title = title
        self.children = children

    def to_config(self):
        # get the serialized type name
        if self.__class__ not in __report_type_names__:
            raise RuntimeError(
                'Report class %r is not registered.' % (self.__class__,))
        type_name = __report_type_names__[self.__class__]

        # get the serialized dict
        ret = super(Report, self).to_config()
        if 'type' in ret:
            raise RuntimeError(
                '`type` is reserved and cannot be used as a serialized value.')
        if ret['children']:
            ret['children'] = [c.to_config() for c in ret['children']]
        else:
            ret.pop('children')
        ret['type'] = type_name
        return ret

    @classmethod
    def get_constructor_kwargs_from_config(cls, config_dict):
        d = super(Report, cls).get_constructor_kwargs_from_config(config_dict)
        if 'children' in d and d['children']:
            serializer = cls.get_json_serializer()
            d['children'] = [
                serializer.from_json_value(v, Report)
                for v in d['children']
            ]
        return d

    @classmethod
    def from_config(cls, config_dict):
        # get the report type
        type_name = config_dict.get('type', None)
        if type_name not in __report_types__:
            raise RuntimeError(
                'Report type %r is not registered.' % (type_name,))
        report_type = __report_types__[type_name]

        # construct the object
        d = report_type.get_constructor_kwargs_from_config(config_dict)
        return report_type(**d)

    def render(self, renderer):
        """Render this report object via specified renderer.

        Parameters
        ----------
        renderer : mlcomp.report.ReportRenderer
            The report renderer.
        """
        name = camel_to_underscore(
            __report_type_names__.get(
                self.__class__,
                self.__class__.__name__
            )
        )
        with renderer.open_scope(name, title=self.title):
            self._render_content(renderer)

    def _render_content(self, renderer):
        """Derived classes might override this to actual render the report."""
        raise NotImplementedError()

register_report_type(Report)
