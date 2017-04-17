# -*- coding: utf-8 -*-
import re

__all__ = ['EXCLUDES_PATTERN', 'is_path_excluded']

#: Default patterns for excluding files / directories
EXCLUDES_PATTERN = re.compile(
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


def is_path_excluded(path, pattern=EXCLUDES_PATTERN):
    """Check whether or not `path` is excluded by `pattern`?
    
    Parameters
    ----------
    path : str
        The path to be checked.
        
    pattern : regex | None
        The pattern of excluded path.
        If `None` is specified, no path will be excluded.
    """
    if pattern:
        return re.match(pattern, path)
    return False
