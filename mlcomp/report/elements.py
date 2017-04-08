# -*- coding: utf-8 -*-
"""Various types of basic report elements."""
from io import BytesIO

import six

from mlcomp.utils import flatten_list
from .base import ReportObject
from .container import Container
from .resource import Resource

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

__all__ = [
    'is_report_element',
    'HTML', 'Text', 'ParagraphText', 'LineBreak', 'InlineMath', 'BlockMath',
    'Image', 'Attachment',
    'TableCell', 'TableRow', 'Table',
    'BokehFigure',
]


class _Element(object):
    """Mixin class to indicate certain class is a report element."""


def is_report_element(o):
    """Check whether or not `o` is a report element class or object."""
    if isinstance(o, six.class_types):
        return issubclass(o, _Element)
    else:
        return isinstance(o, _Element)


class HTML(ReportObject, _Element):
    """HTML element.
    
    Parameters
    ----------
    html : str
        The HTML source.
    """

    def __init__(self, html, **kwargs):
        super(HTML, self).__init__(**kwargs)
        self.html = html


class Text(ReportObject, _Element):
    """Plain text.

    Parameters
    ----------
    text : str
        The plain text.
    """

    def __init__(self, text, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.text = text


class ParagraphText(Text):
    """Paragraph text.
    
    Different from `Text`, the text of a `Paragraph` is guaranteed
    to be displayed in a dedicated paragraph.
    """


class LineBreak(ReportObject, _Element):
    """Line break."""


class _MathEquation(ReportObject):
    """Base class for math equations.

    Parameters
    ----------
    latex : str
        The latex source of this math equation.
    """

    def __init__(self, latex, **kwargs):
        super(_MathEquation, self).__init__(**kwargs)
        self.latex = latex


class InlineMath(_MathEquation, _Element):
    """Inline math equation."""


class BlockMath(_MathEquation, _Element):
    """Block math equation."""


class _ResourceWithTitle(Resource):
    """Resource element with title."""

    def __init__(self, data=None, title=None, **kwargs):
        super(_ResourceWithTitle, self).__init__(data=data, **kwargs)
        self._title = title

    def to_config(self, sort_keys=False):
        ret = super(_ResourceWithTitle, self).to_config(sort_keys=sort_keys)
        if self._title:
            ret['title'] = self._title
        return ret

    @property
    def title(self):
        title = self._title
        if not title and self.path:
            title = self.path.rsplit('/', maxsplit=1)[-1]
        if not title and self.name:
            title = self.name
        return title


class Image(_ResourceWithTitle, _Element):
    """Image resource.
    
    Parameters
    ----------
    data : bytes | PIL.Image.Image
        The binary data of the image, or a PIL image object.
        If an image object is provided, it will be encoded as PNG.
        
    title : str
        Optional title of this image.
        If not specified, will use the filename, or its name as title.
        
    extension : str
        The extension of the image.
        
    content_type : str
        The content-type of the image.
        
    **kwargs
        Other arguments passed to `Resource`.
    """

    def __init__(self, data=None, title=None, extension=None, content_type=None,
                 **kwargs):
        # convert various types of image data into bytes
        if PILImage:
            if isinstance(data, PILImage.Image):
                with BytesIO() as f:
                    data.save(f, format='PNG')
                    f.seek(0)
                    data = f.read()
                    content_type = 'image/png'

        # validate whether `data` is bytes after conversion
        if not isinstance(data, six.binary_type):
            raise TypeError('`data` must be a PIL image, or binary data.')

        # if content-type is not provided or has not been inferred,
        # try to detect the content-type based on data
        if content_type is None:
            try:
                import magic
                content_type = magic.Magic(mime=True).from_buffer(data)
            except ImportError:
                pass

        super(Image, self).__init__(
            data=data, title=title, extension=extension,
            content_type=content_type, **kwargs
        )

    @property
    def extension(self):
        if self._extension is None and self.path is None:
            if self._content_type in ('image/jpeg', 'image/jpg'):
                # The `mimetypes` package sometimes give ".jpe" as the
                # extension for jpg images, which is not a common choice.
                return '.jpg'
        return super(Image, self).extension


class Attachment(_ResourceWithTitle, _Element):
    """Attachment resource.
    
    Parameters
    ----------
    data : bytes
        Binary data of this attachment.
    
    title : str
        Optional title of this attachment.
        If not specified, will use the filename, or its name as title.
        
    **kwargs
        Other arguments passed to `Resource`.
    """

    def __init__(self, data=None, title=None, **kwargs):
        super(Attachment, self).__init__(data=data, title=title, **kwargs)


class TableCell(Container, _Element):
    """Table cell element.
    
    Parameters
    ----------
    children
        The report objects which is contained in this table cell.
        
    rowspan : int
        The rows for this cell to span.
        
    colspan : int
        The columns for this cell to span.
    """

    def __init__(self, children=None, rowspan=None, colspan=None, **kwargs):
        super(TableCell, self).__init__(children=children, **kwargs)
        self.rowspan = rowspan
        self.colspan = colspan


class TableRow(Container, _Element):
    """Table row element.
    
    Parameters
    ----------
    cells
        The table cells contained in this row.
    """

    def __init__(self, cells=None, **kwargs):
        super(TableRow, self).__init__(children=cells, **kwargs)
        for c in self.children:
            if not isinstance(c, TableCell):
                raise TypeError('%r is not a TableCell object.' % (c,))

    def to_config(self, sort_keys=False):
        ret = super(TableRow, self).to_config(sort_keys=sort_keys)
        if 'children' in ret:
            ret['cells'] = ret.pop('children')
        return ret


class Table(ReportObject, _Element):
    """Table element.
    
    Parameters
    ----------
    rows
        The row(s) of the table.
        If a nested list is provided, it will be flatten.
        
    header
        Optional row(s) of the table header.
        If a nested list is provided, it will be flatten.
        
    footer
        Optional row(s) of the table header.
        If a nested list is provided, it will be flatten.
        
    title : str
        Optional title of the table.
        
    name, name_scope : str
        Name and the name scope of this table.
    """

    def __init__(self, rows, header=None, footer=None, title=None,
                 name=None, name_scope=None):
        def parse_row_list(arr):
            if isinstance(arr, TableRow):
                return [arr]
            elif not isinstance(arr, ReportObject):
                ret = []
                for c in flatten_list(arr):
                    if not isinstance(c, TableRow):
                        raise TypeError('%r is not a TableRow.' % (c,))
                    ret.append(c)
                return ret
            else:
                raise TypeError('%r is not TableRow(s).' % (arr,))

        super(Table, self).__init__(name=name, name_scope=name_scope)
        self.rows = parse_row_list(rows)
        self.header = parse_row_list(header) if header else None
        self.footer = parse_row_list(footer) if footer else None
        self.title = title


class BokehFigure(ReportObject, _Element):
    """Bokeh figure element.
    
    Parameters
    ----------
    figure
        The bokeh figure object.
        Required when constructed from fresh.
        
    title : str
        Optional title of this figure.
        
    html : str
        The HTML source for figure containers.
        Required only if deserialized from JSON.
        
    js : Resource
        The JS resource file for figure.
        Required only if deserialized from JSON.
    """

    def __init__(self, figure=None, title=None, html=None, js=None, **kwargs):
        if figure is None:
            if html is None or js is None:
                raise ValueError('`html` and `js` are required if `figure` '
                                 'is not specified.')
        else:
            from bokeh.embed import components
            js, html = components(figure, wrap_script=False)
            js = Resource(js.encode('utf-8'), extension='.js', name='PlotData')

        self.title = title
        self.html = html
        self.js = js
        super(BokehFigure, self).__init__(**kwargs)
