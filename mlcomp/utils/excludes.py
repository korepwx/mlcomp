# -*- coding: utf-8 -*-
import re

import six

__all__ = ['PathExcludes', 'default_path_excludes']


class PathExcludes(object):
    """Class to exclude paths according to patterns.
    
    Parameters
    ----------
    pattern : re.__Regex | str | None
        The pattern of path to be excluded.
        If `None` is specified, no path will be excluded.
    """

    def __init__(self, pattern):
        self.set_pattern(pattern)

    def set_pattern(self, pattern):
        """Set the pattern of excluded paths.
        
        Parameters
        ----------
        pattern : re.__Regex | str | None
            The pattern of path to be excluded.
            If `None` is specified, no path will be excluded.
        """
        if isinstance(pattern, six.string_types):
            pattern = re.compile(pattern)
        self.pattern = pattern

    def is_excluded(self, path):
        """Check whether or not `path` is excluded.
        
        Parameters
        ----------
        path : str
            The path to be checked.
        
        Returns
        -------
        bool
        """
        if self.pattern is None:
            return False
        return re.match(self.pattern, path)

default_path_excludes = PathExcludes(
    re.compile(
        r'''
          # match the start position, or parent directories
          (?:^|.*[/\\])
    
          # the main file pattern
          (?:
            # match excluded directories
            (\.git|\.svn|\.idea|node_modules)(?:$|[/\\].*)
    
            # match excluded files
          | (\.DS_Store)$
          )
        ''',
        re.VERBOSE
    )
)
