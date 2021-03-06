# -*- coding: utf-8 -*-
import codecs
import json
import os
import stat

from mlcomp import __version__
from mlcomp.utils import makedirs
from .base import ReportJsonEncoder, ReportJsonDecoder
from .resource import ResourceManager

__all__ = [
    'ReportSaver', 'REPORT_RESOURCE_DIR', 'REPORT_JSON_FILE',
]

REPORT_RESOURCE_DIR = 'res/'
REPORT_JSON_FILE = 'report.json'


class ReportSaver(object):
    """Saving report object and all its resources to directory.

    A set of methods are needed to be called in order, so as to load
    or save a report object with its resources correctly.  For example,
    for saving a report object:

        report = ReportObject(...)
        report.assign_name_scopes()
        rm = ResourceManager(save_dir=...)
        report.save_resources(rm)
        with codecs.open(..., 'wb', 'utf-8') as f:
            f.write(report.to_json())

    And for loading a report object:

        with codecs.open(..., 'rb', 'utf-8') as f:
            report = ReportObject.from_json(f.read())
        rm = ResourceManager(save_dir=...)
        report.load_resources(rm)

    It would be tedious to write a bunch of code every time to load or
    save a report object.  Thus we provide `ReportSaver` to simplify it.
    Furthermore, it also writes some meta information in additional to
    the report object to the serialized JSON file.

    Parameters
    ----------
    save_dir : str
        The directory where to store JSON serialized file of report,
        as well as to put the resources.

    overwrite : bool
        Whether or not to overwrite existing files at `save_dir`?
        (default is False)
    """

    def __init__(self, save_dir, overwrite=False):
        self.save_dir = os.path.abspath(save_dir)
        self.overwrite = overwrite

    def save_dir_exists(self):
        """Check whether `save_dir` exists and is not an empty directory."""
        if not os.path.exists(self.save_dir):
            return False
        st = os.stat(self.save_dir)
        if stat.S_ISDIR(st.st_mode) and not os.listdir(self.save_dir):
            return False
        return True

    def save(self, report):
        """Save the report object to `save_dir`.

        Parameters
        ----------
        report : ReportObject
            The report object to be saved.

        Raises
        ------
        IOError
            If the save directory already exists.

        Notes
        -----
        This method will change the internal states of `report`.
        """
        if not self.overwrite and self.save_dir_exists():
            raise IOError('%r already exists.' % (self.save_dir,))
        makedirs(self.save_dir, exist_ok=True)
        report.assign_name_scopes()
        rm = ResourceManager(
            os.path.join(self.save_dir, REPORT_RESOURCE_DIR),
            rel_path=REPORT_RESOURCE_DIR
        )
        json_file = os.path.join(self.save_dir, REPORT_JSON_FILE)
        report.save_resources(rm)
        with codecs.open(json_file, 'wb', 'utf-8') as f:
            cnt = {
                'generator': 'mlcomp %s' % __version__,
                'report': report,
            }
            json.dump(cnt, f, cls=ReportJsonEncoder, sort_keys=True)

    def load(self):
        """Load the report object from `save_dir`."""
        json_file = os.path.join(self.save_dir, REPORT_JSON_FILE)
        with codecs.open(json_file, 'rb', 'utf-8') as f:
            cnt = json.load(f, cls=ReportJsonDecoder)
            report = cnt['report']
        rm = ResourceManager(
            os.path.join(self.save_dir, REPORT_RESOURCE_DIR),
            rel_path=REPORT_RESOURCE_DIR
        )
        report.load_resources(rm)
        return report
