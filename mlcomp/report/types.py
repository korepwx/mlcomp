# -*- coding: utf-8 -*-
import copy
from contextlib import contextmanager

from qualname import qualname
import six

from mlcomp.utils import import_string, ContextStack

__all__ = [
    'ReportTypes', 'get_default_report_types', 'default_report_types',
]


class ReportTypes(object):
    """Context to hold report object type configs.
    
    When "safe-mode" is enabled (which is by default turned on), a report 
    object of customized type cannot be loaded by its full class name.
    Instead, it must be configured in a `ReportTypes` context.
    
    Note that all report types in `mlcomp.report` package are configured
    implicitly.
    
    Parameters
    ----------
    mappings : dict[str, class]
        The mapping from type name to type object.
        
        If multiple names are mapped to a same class, the inverse mapping
        will choose any one of the configured classes.
        
    safe_mode : bool
        Whether or not the enable the safe mode? (Default True)
    """

    def __init__(self, mappings=None, safe_mode=True):
        self.mappings = dict(mappings or ())
        self.reverse_map = {v: k for k, v in six.iteritems(self.mappings)}
        self.safe_mode = safe_mode

    @contextmanager
    def as_default(self):
        """Push this to the context stack."""
        _report_types_stack.push(self)
        try:
            yield self
        finally:
            _report_types_stack.pop()

    def copy(self, mappings=None, safe_mode=None):
        """Copy and construct a new `ObjectTypes` context."""
        if mappings is not None:
            mappings2 = copy.copy(self.mappings)
            mappings2.update(mappings)
            mappings = mappings2
        else:
            mappings = self.mappings
        if safe_mode is None:
            safe_mode = self.safe_mode
        return ReportTypes(mappings, safe_mode)

    def name_to_type(self, name):
        """Find a report object type according to its type name.
        
        Parameters
        ----------
        name : str
            The type name of the report object.
            
        Raises
        ------
        KeyError
            If the name is not configured.
            
        TypeError
            If the loaded type is not a report object type.
        """
        from .base import ReportObject
        rtype = None
        if name in self.mappings:
            rtype = self.mappings[name]
        if rtype is None and '.' not in name and ':' not in name:
            try:
                rtype = import_string('mlcomp.report.%s' % (name,))
            except ImportError:
                pass
        if rtype is None and not self.safe_mode:
            try:
                rtype = import_string(name)
            except ImportError:
                pass
        if rtype is None:
            raise KeyError('Type name %r is not configured.' % (name,))
        elif not isinstance(rtype, six.class_types) or \
                not issubclass(rtype, ReportObject):
            raise TypeError('Type %r is not a report object type.' % (rtype,))
        return rtype

    def type_to_name(self, rtype):
        """Find a report object type name according to its type.
        
        Parameters
        ----------
        rtype : class
            The type of the report object.
            
        Raises
        ------
        TypeError
            If `rtype` is not a report object.
    
        KeyError
            If the report object type is not configured.
        """
        from .base import ReportObject
        if not isinstance(rtype, six.class_types) or \
                not issubclass(rtype, ReportObject):
            raise TypeError('%r is not a report object type.' % (rtype,))
        if rtype in self.reverse_map:
            return self.reverse_map[rtype]
        type_name = '%s.%s' % (rtype.__module__, qualname(rtype))
        if type_name.startswith('mlcomp.report.'):
            return type_name.rsplit('.', 1)[-1]
        if not self.safe_mode:
            return type_name
        raise KeyError('Type %r is not configured.' % (rtype,))


def get_default_report_types():
    """Get the `ObjectTypes` instance at the top of context stack.
    
    Returns
    -------
    ReportTypes
    """
    return _report_types_stack.top()


@contextmanager
def default_report_types(mappings=None, safe_mode=None):
    """Open a scoped context with mappings of object types."""
    ctx = get_default_report_types().copy(mappings, safe_mode=safe_mode)
    with ctx.as_default():
        yield ctx

_report_types_stack = ContextStack(initial_factory=ReportTypes)
