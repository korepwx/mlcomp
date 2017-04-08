# -*- coding: utf-8 -*-
"""Various types of basic report elements."""
from io import BytesIO

import six

from .base import ReportObject
from .resource import Resource

__all__ = [
    'is_report_element',
    'HTML', 'Text', 'ParagraphText', 'LineBreak', 'InlineMath', 'BlockMath',
    'Image',
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


class Image(Resource, _Element):
    """Image resource element.
    
    Parameters
    ----------
    data : bytes | PIL.Image.Image
        The binary data of the image, or a PIL image object.
        If an image object is provided, it will be encoded as PNG.
        
    extension : str
        The extension of the image.
        
    content_type : str
        The content-type of the image.
    """

    def __init__(self, data=None, extension=None, content_type=None, **kwargs):
        # convert various types of image data into bytes
        try:
            from PIL import Image as PILImage
            if isinstance(data, PILImage.Image):
                with BytesIO() as f:
                    data.save(f, format='PNG')
                    f.seek(0)
                    data = f.read()
                    content_type = 'image/png'
        except ImportError:
            pass

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
            data=data, extension=extension, content_type=content_type, **kwargs)

    @property
    def extension(self):
        if self._extension is None and self.path is None:
            if self._content_type in ('image/jpeg', 'image/jpg'):
                # The `mimetypes` package sometimes give ".jpe" as the
                # extension for jpg images, which is not a common choice.
                return '.jpg'
        return super(Image, self).extension
