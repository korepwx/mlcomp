# -*- coding: utf-8 -*-
from mlcomp.report import Report


class MyReport(Report):

    def __init__(self, c, title, children=None):
        super(MyReport, self).__init__(title, children)
        self.c = c

    def to_config(self, report_type_names=None):
        ret = super(MyReport, self).to_config(report_type_names)
        ret['c'] = self.c
        return ret
