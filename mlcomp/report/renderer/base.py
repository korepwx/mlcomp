# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

from ..base import Report

__all__ = ['Renderer']


class RenderScope(object):
    """Rendering scope object.

    Parameters
    ----------
    name : str
        Name of this scope.

    path : str
        Path of this scope (which is a joint of parent names and
        the name of this scope, separated by '/').

    title : str
        Optional title of this scope.
    """

    def __init__(self, name, path, title=None):
        self.name = name
        self.path = path
        self.title = title
        # allocated names of this scope
        self._names = set()
        # track the next available index for each name
        self._name_idx_tracker = {}

    def allocate(self, name):
        """Allocate a unique name."""
        if name in self._names:
            idx = self._name_idx_tracker.get(name, 1)
            while True:
                n = '%s_%d' % (name, idx)
                if n not in self._names:
                    self._name_idx_tracker[name] = idx + 1
                    name = n
                    break
                idx += 1
        self._names.add(name)
        return name


class Renderer(object):
    """Base class for all report renderer."""

    def __init__(self):
        # stack of opened scopes
        self._scopes = [RenderScope('', '')]

    @property
    def scope_name(self):
        """Name of the current active scope."""
        return self._scopes[-1].name

    @property
    def scope_path(self):
        """Path of the current active scope."""
        return self._scopes[-1].path

    @contextmanager
    def open_scope(self, name, title=None):
        """Open a nested scope.

        Parameters
        ----------
        name : str
            Name of the scope.

        title : str
            Optional title for this scope.

        Returns
        -------
        str
            De-duplicated name for this scope.
        """
        if not name:
            raise ValueError('`name` cannot be empty.')
        name = self._scopes[-1].allocate(name)
        path = self._scopes[-1].path
        if path:
            path += '/' + name
        else:
            path = name
        scope = RenderScope(name, path, title=title)
        self._scopes.append(scope)
        try:
            yield name
        finally:
            self._scopes.pop()

    def render(self, *reports):
        """Render reports via this renderer.

        Parameters
        ----------
        *reports : tuple[Report]
            Report objects to be rendered.

        Returns
        -------
        self
        """
        for report in reports:
            report.render(self)
        return self

    def allocate_name(self, name):
        """Allocate a unique name for whatever usage.

        The allocated name will be ensured to unique among all
        other names (including scope names, file base names and
        whatever names produced by `allocate_name`) under the
        current active scope.

        Parameters
        ----------
        name : str
            The desired name.

        Returns
        -------
        str
            De-duplicated name.
        """
        return self._scopes[-1].allocate(name)

    def allocate_filename(self, filename):
        """Allocate a unique filename.

        The basename of the allocated filename will be ensured
        to unique among all other names (including scope names,
        file base names and whatever names produced by
        `allocate_name`) under the current active scope.

        Parameters
        ----------
        filename : str
            The desired filename.  Indices will be appended to
            the basename in order for de-duplication.

        Returns
        -------
        str
            De-duplicated filename.
        """
        basename, ext = os.path.splitext(filename)
        basename = self.allocate_name(basename)
        return ''.join((basename, ext))

    def __enter__(self):
        self.begin_document()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_document()
        self.close()

    def begin_document(self):
        """Begin to render the report.

        Derived classes may override this to write report headers.
        This method will be called automatically with a context manager.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def end_document(self):
        """Finish to render the report.

        Derived classes may override this to write report endings.
        This method will be called automatically with a context manager.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def close(self):
        """Close all files and resources opened by this renderer."""
        raise NotImplementedError()

    def write_text(self, text):
        """Write a piece of text.

        The text should be interpreted as plain text, and should be rendered
        in the most suitable way, such that the paragraphs and indents are
        preserved in resulted document.

        Parameters
        ----------
        text : str
            The plain text.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def write_html(self, html):
        """Write a piece of HTML source code.

        The renderer should try its best to display the HTML code in the
        most suitable way.

        Parameters
        ----------
        html : str
            The html source code to be displayed.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def write_image(self, image, title=None, content_type=None):
        """Write an image.

        Parameters
        ----------
        image : PIL.Image | io.RawIOBase | bytes
            The image to be displayed.

        content_type : str
            Content type of the image, if the image binary contents instead
            of a PIL image instance is provided.

        title : str
            Optional title of the image.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def write_attachment(self, data, filename, title=None, content_type=None):
        """Write an attachment.

        The attachment may be rendered as a link that allow the user to
        download the file through browser.

        Parameters
        ----------
        data : io.RawIOBase | bytes
            Binary content or input stream of this attachment.

        filename : str
            File name of this attachment.

        title : str
            Alternative title of this attachment, other than the filename.

        content_type : str
            Content type of this attachment.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def write_table(self, data, title=None):
        """Write a table.

        Parameters
        ----------
        data : pandas.DataFrame
            The table data to be displayed.

        title : str
            Optional title of the table.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def write_figure(self, fig, title=None):
        """Write a figure.

        Parameters
        ----------
        fig : matplotlib.figure.Figure | bokeh.model.Model
            The figure to be displayed.

        title : str
            Optional title of the figure.

        Returns
        -------
        self
        """
        raise NotImplementedError()
