# -*- coding: utf-8 -*-
import copy
import inspect

import six
from qualname import qualname

from mlcomp.utils import AutoReprObject, camel_to_underscore, import_string

__all__ = ['Report']


class Report(AutoReprObject):
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

    def __init__(self, title=None, children=None):
        self.title = title
        self.children = children

    def to_config(self, report_type_names=None):
        """Get a dict of attribute values for this report.

        Parameters
        ----------
        report_type_names : dict[class, str]
            Additional mapping from report type to type name.

            If not specified, any custom report types will be mapped
            to its qualified name, thus may cause trouble when loading
            these report objects via `from_config` in safe-mode.

        Returns
        -------
        dict[str, any]
            The attribute value dict, which can be used to construct
            a report object via `Report.from_config`.
        """
        # get the serialized type name
        if report_type_names and self.__class__ in report_type_names:
            type_name = report_type_names[self.__class__]
        else:
            type_name = '%s.%s' % (
                self.__class__.__module__,
                qualname(self.__class__)
            )
            if type_name.startswith('mlcomp.report.'):
                type_name = type_name.rsplit('.', 1)[1]

        # get the serialized dict
        ret = {'type': type_name}
        if self.title:
            ret['title'] = self.title
        if self.children:
            ret['children'] = [
                c.to_config(report_type_names) for c in self.children
            ]
        return ret

    @classmethod
    def process_config_dict(cls, config_dict, safe_mode, report_types):
        """Process the `config_dict` before constructing report object."""
        if 'children' in config_dict and config_dict['children']:
            config_dict['children'] = [
                Report.from_config(c, safe_mode, report_types)
                for c in config_dict['children']
            ]
        return config_dict

    @classmethod
    def from_config(cls, config_dict, safe_mode=True, report_types=None):
        """Construct a report object from `config_dict`.

        Parameters
        ----------
        config_dict : dict[str, any]
            The dict of attribute values.

        safe_mode : bool
            Whether or not to allow importing arbitrary report class
            according to `type` in `config_dict`?

            If `safe_mode` is set to True, this is not allowed.

        report_types : dict[str, class]
            Additional mapping from report type name to classes.

            This can allow loading custom report classes when `safe_mode`
            is turned on.
        """
        # get the report type
        type_name = config_dict['type']
        if report_types and type_name in report_types:
            rtype = report_types[type_name]
        elif '.' not in type_name and ':' not in type_name:
            try:
                rtype = import_string('mlcomp.report.%s' % (type_name,))
            except ImportError:
                raise KeyError(
                    'Type name %r is not specified in `report_types`.' %
                    (type_name,)
                )
        elif safe_mode:
            raise KeyError(
                'Type name %r is not specified in `report_types`.' %
                (type_name,)
            )
        else:
            rtype = import_string(type_name)

        if not isinstance(rtype, six.class_types) or \
                not issubclass(rtype, Report):
            raise TypeError('%r is not a Report class.' % (rtype,))

        # construct the object
        kwargs = copy.copy(config_dict)
        kwargs.pop('type')
        kwargs = rtype.process_config_dict(kwargs, safe_mode, report_types)
        return rtype(**kwargs)

    def render(self, renderer):
        """Render this report object via specified renderer.

        Parameters
        ----------
        renderer : mlcomp.report.ReportRenderer
            The report renderer.
        """
        name = camel_to_underscore(self.__class__.__name__)
        with renderer.open_scope(name, title=self.title):
            self._render_content(renderer)

    def _render_content(self, renderer):
        """Derived classes might override this to actual render the report."""
        raise NotImplementedError()
