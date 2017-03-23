# -*- coding: utf-8 -*-
import json
from datetime import datetime

import numpy as np
import pandas as pd
import six

__all__ = ['JsonEncoder', 'JsonHelper']


class JsonEncoder(json.JSONEncoder):
    """Extended JSON encoder with support of the following types:

    *   numpy.ndarray       -> JSON array
    *   pandas.DataFrame    -> JSON object (via `to_dict()`)
    *   datetime.datetime   -> JSON number (local timestamp in milliseconds)
    """

    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, pd.DataFrame):
            return o.to_dict()
        if isinstance(o, datetime):
            return o.timestamp() * 1000
        return super(JsonEncoder, self).default(o)


class JsonHelper(object):
    """Helper class to convert JSON value back to desired type."""

    def get_numpy_array(self, v):
        if isinstance(v, list):
            return np.asarray(v)
        if isinstance(v, np.ndarray):
            return v
        raise TypeError('%r cannot be converted to numpy array.' % (v,))

    def get_data_frame(self, v):
        if isinstance(v, dict):
            return pd.DataFrame.from_dict(v)
        if isinstance(v, pd.DataFrame):
            return v
        raise TypeError('%r cannot be converted to data frame.' % (v,))

    def get_datetime(self, v):
        if isinstance(v, six.integer_types + (float,)):
            return datetime.fromtimestamp(v / 1000.0)
        if isinstance(v, datetime):
            return v
        raise TypeError('%r cannot be converted to datetime.' % (v,))
