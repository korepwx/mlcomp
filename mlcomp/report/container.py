# -*- coding: utf-8 -*-
from mlcomp.utils import flatten_list
from .base import ReportObject
from .persist import ReportSaver

__all__ = ['Container', 'Report']


class Container(ReportObject):
    """Report object container.

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


class Report(Container):
    """Main report container.
     
    This container class is mainly used for composing the whole report,
    as contrary to `Container` class which is usually used as base class
    of other report classes.  Besides the basic functions of a report
    container, it also provides two convenient methods `load` and `save`,
    as a thin wrapper upon `ReportSaver`.
    """

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

    def add(self, *children):
        """Add report object(s) into this container.

        Parameters
        ----------
        *children
            The report object(s) to be added into this container.
            If nested list(s) are provided, they will be flatten.
        """
        super(Report, self)._add(*children)

    def remove(self, *children):
        """Remove report object(s) from this container.

        Parameters
        ----------
        *children
            The report object(s) to be removed from this container.
            If nested list(s) are provided, they will be flatten.

            Will not raise error if specified children does not exist.
        """
        super(Report, self)._remove(*children)
