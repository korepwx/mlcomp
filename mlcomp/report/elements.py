# -*- coding: utf-8 -*-
import mimetypes
import os

import io

from mlcomp.utils import AutoReprObject

__all__ = [
    'Element', 'Block', 'Text', 'InternalLink', 'ExternalLink', 'HTML',
    'Image', 'Attachment', 'Table', 'Figure',
]


def is_pil_image(image):
    """Test whether or not `image` is a PIL image."""
    try:
        from PIL.Image import Image as PILImage
        return isinstance(image, PILImage)
    except ImportError:
        return False


class Element(AutoReprObject):
    """Base class for all rendered element of a report.

    Parameters
    ----------
    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """
    __repr_attributes__ = ()
    __repr_value_length__ = 32

    def __init__(self, anchor=None):
        self.anchor = anchor


class Block(Element):
    """A rendered block of a report.

    Parameters
    ----------
    title : str
        Title of this block.

    children : collections.Iterable[ReportElement]
        Child elements of this block.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, title, children=None, anchor=None):
        super(Block, self).__init__(anchor=anchor)
        self.title = title
        self.items = list(children) if children else []

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def add(self, element):
        """Add a report element to this block."""
        self.items.append(element)


class Text(Element):
    """A rendered text of a report.

    Parameters
    ----------
    text : str
        The report text.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, text, anchor=None):
        super(Text, self).__init__(anchor=anchor)
        self.text = text


class InternalLink(Element):
    """A rendered internal link of a report.

    Parameters
    ----------
    text : str
        The link text.

    target : str
        The target anchor.
    """

    def __init__(self, text, target):
        super(InternalLink, self).__init__()
        self.text = text
        self.target = target


class ExternalLink(Element):
    """A rendered external link of a report.

    Parameters
    ----------
    text : str
        The link text.

    url : str
        The target URL.
    """

    def __init__(self, text, url):
        super(ExternalLink, self).__init__()
        self.text = text
        self.url = url


class HTML(Element):
    """A rendered HTML of a report.

    Parameters
    ----------
    source : str
        The report HTML source.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, source, anchor=None):
        super(HTML, self).__init__(anchor=anchor)
        self.source = source


class _File(Element):
    """Base class for a rendered file of a report.

    Parameters
    ----------
    data: bytes
        Binary content of this file.

    title : str
        Title of this file.

    filename : str
        File name of this file.

    extension : str
        Extension of this file.

    content_type : str
        Mime type of this file.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, data, title=None, filename=None, extension=None,
                 content_type=None, anchor=None):
        super(_File, self).__init__(anchor=anchor)
        if extension is None:
            if filename is not None:
                extension = os.path.splitext(filename)[1]
            else:
                extension = mimetypes.guess_extension(content_type)
                if extension is None:
                    raise RuntimeError('Unknown mime type %r.' % content_type)
        self.data = data
        self.title = title
        self.filename = filename
        self.extension = extension
        self.content_type = content_type

    @property
    def title_or_filename(self):
        """Get the title of the file, or the filename if title not specified."""
        return self.title or self.filename


class Image(_File):
    """A rendered image of a report.

    Parameters
    ----------
    image : PIL.Image.Image | bytes | io.IOBase
        PIL image object, the content of image as bytes, or a file-like
        object that can read out the content of image.

    title : str
        Title of the image.

    content_type : str
        Content-type of the image, required if only the content of the image
        rather than a PIL image object is specified.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, image, title=None, content_type=None, anchor=None):
        ext = None
        if is_pil_image(image):
            with io.BytesIO() as f:
                image.save(f, format='PNG')
                f.seek(0)
                img = f.read()
            content_type = 'image/png'
            ext = '.png'
        elif hasattr(image, 'read'):
            img = image.read()
            if not isinstance(img, bytes):
                raise TypeError('Required to read bytes but got string.')
        elif isinstance(image, bytes):
            img = image
        else:
            raise TypeError('%r cannot be rendered as image.' % (image,))

        if content_type is None:
            raise ValueError('Content-type of the image is required.')

        super(Image, self).__init__(
            img, title=title, extension=ext, content_type=content_type,
            anchor=anchor
        )


class Attachment(_File):
    """A rendered attachment of a report.

    Parameters
    ----------
    data : bytes | io.IOBase
        Bytes of the attachment, or a file-like object.

    title : str
        Title of the attachment.

    content_type : str
        Content-type of the attachment.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, data, filename, title=None, content_type=None,
                 anchor=None):
        if hasattr(data, 'read'):
            cnt = data.read()
            if not isinstance(cnt, bytes):
                raise TypeError('Required to read bytes but got string.')
        elif isinstance(data, bytes):
            cnt = data
        else:
            raise TypeError('%r cannot be rendered as attachment.' % (data,))

        if content_type is None:
            content_type = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = 'application/octet-stream'

        super(Attachment, self).__init__(
            cnt, title=title, filename=filename, content_type=content_type,
            anchor=anchor
        )


class Table(Element):
    """A rendered table of a report.

    Parameters
    ----------
    data : pandas.DataFrame
        Pandas data frame, as the table content.

    title : str
        Title of this data frame.

    anchor : str
        Anchor name of this element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, data, title=None, anchor=None):
        super(Table, self).__init__(anchor=anchor)
        self.data = data
        self.title = title


class Figure(Element):
    """A rendered figure of a report.

    Parameters
    ----------
    figure : bokeh.model.Model
        A Boheh figure object, as the figure.

    title : str
        Title of this figure.

    anchor : str
        Anchor name of the element.
        If specified, this element can be referenced by internal links.
    """

    def __init__(self, figure, title=None, anchor=None):
        super(Figure, self).__init__(anchor=anchor)
        self.figure = figure
        self.title = title
