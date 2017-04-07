# -*- coding: utf-8 -*-

"""Various types of basic report elements."""

from .base import ReportObject

__all__ = [
    'HTML',
]


class HTML(ReportObject):
    """HTML report element."""

    def __init__(self, html):
        super(HTML, self).__init__()
        self.html = html
