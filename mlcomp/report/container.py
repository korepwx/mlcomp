# -*- coding: utf-8 -*-
from mlcomp.utils import flatten_list
from .base import ReportObject
from .persist import ReportSaver

__all__ = ['Container', 'Group', 'Report']


class Container(ReportObject):
    """Report container object.
    
    A container object contains other report objects as children.
    It is usually inherited by more complicated report object types.

    Parameters
    ----------
    children
        The child report objects of this container.
        If a nested list is provided, it will be flatten.

    name, name_scope : str
        Name and the scope of this container.
    """

    def __init__(self, children=None, name=None, name_scope=None):
        self.children = []  # type: list[ReportObject]
        if isinstance(children, ReportObject):
            self._add(children)
        elif children:
            self._add(*children)
        super(Container, self).__init__(name=name, name_scope=name_scope)

    def gather_children(self):
        return super(Container, self).gather_children() + self.children

    def _add(self, *children):
        for c in flatten_list(children):
            if not isinstance(c, ReportObject):
                raise TypeError('%r is not a report object.' % (c,))
            self.children.append(c)

    def _remove(self, *children):
        for c in flatten_list(children):
            if not isinstance(c, ReportObject):
                raise TypeError('%r is not a report object.' % (c,))
            try:
                self.children.remove(c)
            except ValueError:
                pass


class Group(Container):
    """A report group.
    
    A report group is a container whose children can be further changed
    via public method `add` and `remove`.
    """

    def add(self, *children):
        """Add report object(s) into this container.

        Parameters
        ----------
        *children
            The report object(s) to be added into this container.
            If nested list(s) are provided, they will be flatten.
        """
        super(Group, self)._add(*children)

    def remove(self, *children):
        """Remove report object(s) from this container.

        Parameters
        ----------
        *children
            The report object(s) to be removed from this container.
            If nested list(s) are provided, they will be flatten.

            Will not raise error if specified children does not exist.
        """
        super(Group, self)._remove(*children)


class Report(Group):
    """The top-most report object.
    
    A Report object is a specialized report Group, which often represents
    a whole report file.  It carries additional information, for example,
    `title` of the report.
    
    Parameters
    ----------
    children
        The child report objects of this container.
        If a nested list is provided, it will be flatten.
        
    title : str
        Optional title for this report.
    """

    def __init__(self, children=None, title=None, **kwargs):
        super(Report, self).__init__(children=children, **kwargs)
        self.title = title

    def save(self, save_dir, overwrite=False):
        """Save this report to `save_dir`.

        Parameters
        ----------
        save_dir : str
            The directory where to store JSON serialized file of report,
            as well as to put the resources.
            
        overwrite : bool
            Whether or not to overwrite existing files at `save_dir`?
            (default is False)
        """
        ReportSaver(save_dir, overwrite=overwrite).save(self)

    @staticmethod
    def load(save_dir):
        """Load report from `save_dir`."""
        return ReportSaver(save_dir).load()
