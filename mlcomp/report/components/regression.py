# -*- coding: utf-8 -*-
import itertools
import json
from collections import OrderedDict

import numpy as np
import pandas as pd
from sklearn.metrics import (mean_absolute_error,
                             mean_squared_error,
                             explained_variance_score, r2_score)
from sklearn.utils.multiclass import unique_labels

from mlcomp.utils import JsonEncoder
from .table_factory import *
from ..elements import *

__all__ = [
    'regression_summary',
    'regression_result_attachment',
]


def regression_report_data_frame(truth, predict, label, per_target=True,
                                 target_names=None):
    # check the arguments
    if predict.shape != truth.shape:
        raise TypeError('Shape of `predict` does not match `truth`.')
    if label is not None and len(label) != len(truth):
        raise TypeError('Size of `label` != size of `truth`.')

    # generate the target names
    target_shape = truth.shape[1:]
    if not len(target_shape):
        target_shape = (1,)

    if not per_target:
        target_names = None
    elif target_names is not None:
        target_names = np.asarray([str(t) for t in target_names])
    else:
        target_names = np.asarray([
            '[%s]' % ','.join(str(s) for s in indices)
            for indices in itertools.product(
                *(range(i) for i in target_shape)
            )
        ])

    if target_names is not None and target_names.shape != target_shape:
        raise TypeError('Shape of `targets` does not match that of `truth`.')

    # flatten the dimensions in truth and target data to match the targets
    truth = truth.reshape([len(truth), -1])
    predict = predict.reshape([len(predict), -1])

    # generate the data frame
    MSE, MAE, R2, EVS, SUPPORT = (
        'Squared Error',
        'Absolute Error',
        'R2 Score',
        'Explained Variance',
        'Support'
    )
    data = OrderedDict([
        (MSE, []),
        (MAE, []),
        (R2, []),
        (EVS, []),
        (SUPPORT, [])
    ])
    index = []

    def add_row(y_true, y_pred, target=None, label=None):
        names = tuple(v for v in (target, label) if v is not None)
        if len(names) > 1:
            index.append(names)
        else:
            index.append(names[0])
        data[MSE].append(mean_squared_error(y_true, y_pred))
        data[MAE].append(mean_absolute_error(y_true, y_pred))
        data[R2].append(r2_score(
            y_true, y_pred, multioutput='uniform_average'))
        data[EVS].append(explained_variance_score(y_true, y_pred))
        data[SUPPORT].append(len(y_true))

    if target_names is None:
        if label is None:
            add_row(truth, predict, label='total')
            index = pd.Index(index)
        else:
            for lbl in unique_labels(label):
                mask = (label == lbl)
                add_row(truth[mask], predict[mask], label=lbl)
            add_row(truth, predict, label='total')
            index = pd.Index(index, name='Label')
    else:
        if label is None:
            for i, t in enumerate(target_names):
                add_row(truth[:, i], predict[:, i], target=t)
            add_row(truth, predict, target='total')
            index = pd.Index(index, name='Target')
        else:
            for i, t in enumerate(target_names):
                for lbl in unique_labels(label):
                    mask = (label == lbl)
                    add_row(truth[mask][:, i], predict[mask][:, i],
                            target=t, label=lbl)
            add_row(truth, predict, target='', label='total')
            index = pd.MultiIndex.from_tuples(index, names=['Target', 'Label'])

    return pd.DataFrame(data=data, index=index)


def regression_summary(truth, predict, label=None, per_target=True,
                       target_names=None, title=None):
    """Regression result summary table.

    Parameters
    ----------
    truth : np.ndarray
        Ground truth (correct) target values.

    predict : np.ndarray
        Predicted target values.

    label : np.ndarray | list
        If specified, will compute the regression scores for each label class.

    per_target : bool
        Whether or not to compute the regression score for each dimension?
        (default True)

    target_names : np.ndarray | list
        Name of each dimension in regression results.

        If not specified, will use the coordinate of each dimension, e.g.,
        "(0,0,0)".

    title : str
        Optional title of this regression summary table.
    """
    ret = data_frame_to_table(
        regression_report_data_frame(
            truth=truth,
            predict=predict,
            label=label,
            per_target=per_target,
            target_names=target_names,
        ),
        title=title
    )
    # make the total row as footer
    if len(ret.rows) > 1:
        ret.footer = [ret.rows.pop()]
        if ret.header[0].children[0].colspan == 2:
            # when 'Target' and 'Label' both exists,
            # we should make the 'total' colspan as 2
            ret.footer[0].children[1].colspan = 2
            del ret.footer[0].children[0]
    return ret


def regression_result_attachment(truth, predict, title=None, link_only=False):
    """Regression result attachment.

    Parameters
    ----------
    truth : np.ndarray
        Ground truth (correct) target values.

    predict : np.ndarray
        Predicted target values.

    title : str
        Optional title of this attachment.

    link_only : bool
        Whether or not to render only link of this attachment?
        (default False)

    Returns
    -------
    Attachment
        The regression result as an attachment of gzipped JSON file.
    """
    cnt = json.dumps(
        {'truth': truth.tolist(), 'predict': predict.tolist()},
        cls=JsonEncoder,
    )
    return Attachment(
        cnt.encode('utf-8'), title=title, link_only=link_only,
        extension='.json', gzip_compress=True, name='regression_result'
    )
