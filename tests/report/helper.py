# -*- coding: utf-8 -*-
import six


def to_config(report, recursive=True):
    def f(o):
        if isinstance(o, list):
            return [f(v) for v in o]
        elif isinstance(o, dict):
            return {k: f(v) for k, v in six.iteritems(o)}
        elif hasattr(o, 'to_config'):
            return f(o.to_config())
        return o

    if recursive:
        return f(report.to_config())
    return report.to_config()
