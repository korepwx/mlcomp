# -*- coding: utf-8 -*-
import codecs
import json
import os
from contextlib import contextmanager

import six

from .base import Renderer

__all__ = ['JsonRenderer']


class JsonRenderer(Renderer):
    """Renders reports into JSON file.

    This renderer produces JSON file for given reports, which can be parsed
    and displayed by the ML Board web application.
    """

    def __init__(self, json_file, resource_dir):
        super(JsonRenderer, self).__init__()
        self.json_file = os.path.abspath(json_file)
        self.resource_dir = os.path.abspath(resource_dir)
        self._res_relpath = os.path.relpath(
            self.resource_dir, os.path.dirname(self.json_file))
        self._json_root = None
        self._json_stack = None

    def begin_document(self):
        """Begin to render the report.

        Derived classes may override this to write report headers.
        This method will be called automatically with a context manager.

        Returns
        -------
        self
        """
        self._json_root = []
        self._json_stack = [self._json_root]
        return self

    def end_document(self):
        """Finish to render the report.

        Derived classes may override this to write report endings.
        This method will be called automatically with a context manager.

        Returns
        -------
        self
        """
        self._json_stack = [self._json_root]
        return self

    def close(self):
        """Close all files and resources opened by this renderer."""
        obj = json.dumps(self._json_root)
        with codecs.open(self.json_file, 'wb', 'utf-8') as f:
            f.write(obj)
        self._json_root = None
        self._json_stack = None

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
        with super(JsonRenderer, self).open_scope(name, title=title) as scope:
            json_scope = {
                'type': 'scope',
                'name': scope,
                'children': []
            }
            if title is not None:
                json_scope['title'] = title
            self._json_stack[-1].append(json_scope)
            self._json_stack.append(json_scope['children'])
            try:
                yield scope
            finally:
                self._json_stack.pop()

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
        if not isinstance(text, six.string_types):
            raise TypeError('`text` %r is not a string.' % (text,))
        self._json_stack[-1].append({
            'type': 'text',
            'data': text
        })
        return self

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
        self._json_stack[-1].append({
            'type': 'html',
            'data': html
        })
        return self

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
