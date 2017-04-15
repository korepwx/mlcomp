# -*- coding: utf-8 -*-
from collections import OrderedDict
from gzip import GzipFile
from io import BytesIO

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score,
                             precision_recall_curve,
                             precision_recall_fscore_support)
from sklearn.utils.multiclass import unique_labels

from mlcomp.utils import wrap_text_writer
from .table_factory import *
from ..elements import *

__all__ = [
    'binary_classification_auc_curve',
    'classification_summary',
    'classification_result_attachment',
]


def binary_classification_auc_curve(y_true, y_prob, title=None):
    """Binary classification AUC curve.
    
    Parameters
    ----------
    y_true : numpy.ndarray
        Ground truth (correct) target values.

    y_prob : numpy.ndarray
        Estimated probabilities for each target to be each class.

    title : str
        Optional title of this AUC curve figure.
    """
    p1, r1, th = precision_recall_curve(y_true, y_prob)
    area1 = average_precision_score(y_true, y_prob)
    y_true = 1 - y_true
    y_prob = 1. - y_prob
    p0, r0, th = precision_recall_curve(y_true, y_prob)
    area0 = average_precision_score(y_true, y_prob)

    chart = {
        'legend': {
            'horizontalAlign': 'center',
            'verticalAlign': 'top',
            'fontSize': 12,
        },
        'axisX': {
            'title': 'Recall',
            'minimum': 0,
            'maximum': 1.05,
            'gridColor': '#ccc',
            'gridThickness': 1,
        },
        'axisY': {
            'title': 'Precision',
            'minimum': 0,
            'maximum': 1.05,
            'gridColor': '#ccc',
            'gridThickness': 1,
        },
        'data': [
            {
                'name': 'AUC curve of class 0 (area=%.4f)' % area0,
                'showInLegend': True,
                'type': 'line',
                'dataPoints': [
                    {'x': x, 'y': y} for x, y in zip(r0, p0)
                ]
            },
            {
                'name': 'AUC curve of class 1 (area=%.4f)' % area1,
                'showInLegend': True,
                'type': 'line',
                'dataPoints': [
                    {'x': x, 'y': y} for x, y in zip(r1, p1)
                ]
            }
        ]
    }
    if title:
        chart['title'] = {'text': title, 'fontSize': 24}

    return CanvasJS(data=chart)


def classification_summary(y_true, y_pred, labels=None, target_names=None,
                           title=None):
    """Classification result summary table.
    
    Parameters
    ----------
    y_true : numpy.ndarray
        Ground truth (correct) target values.

    y_pred : numpy.ndarray
        Predicted target values.
        
    labels : np.ndarray | list
        Array of all labels.  If not specified, will be inferred from
        `y_true` and `y_pred`.  This argument should be specified if
        not all labels appear in the test data.
        
    target_names : collections.Iterable[any]
        Optional alternative names for the `labels`.

    title : str
        Optional title of this summary table.
    """

    if labels is None:
        labels = unique_labels(y_true, y_pred)
    if target_names is None:
        target_names = [str(i) for i in labels]

    p, r, f1, s = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels
    )

    # compute the average of these scores.
    p_avg = np.average(p, weights=s)
    r_avg = np.average(r, weights=s)
    f1_avg = np.average(f1, weights=s)
    s_sum = np.sum(s)

    # compose the data frame
    def concat(a, b):
        return np.concatenate([a, [b]])
    data = OrderedDict([
        ('Precision', concat(p, p_avg)),
        ('Recall', concat(r, r_avg)),
        ('F1-Score', concat(f1, f1_avg)),
        ('Support', concat(s, s_sum)),
    ])

    summary = pd.DataFrame(data=data, columns=list(data.keys()),
                           index=target_names + ['avg / total'])
    return dataframe_to_table(summary, title=title)


def classification_result_attachment(y_true, y_pred, y_prob, title=None,
                                     link_only=False):
    """Cassification result attachment.
    
    Parameters
    ----------
    y_true : numpy.ndarray
        Ground truth (correct) target values.

    y_pred : numpy.ndarray
        Predicted target values.
        
    y_prob : numpy.ndarray
        Estimated probabilities for each target to be each class.
        
    title : str
        Optional title of this attachment.

    link_only : bool
        Whether or not to render only link of this attachment?
        (default False)
    """
    df = pd.DataFrame(OrderedDict([
        ('y_true', y_true),
        ('y_pred', y_pred),
        ('y_prob', y_prob),
    ]))
    with BytesIO() as f:
        with GzipFile(fileobj=f, mode='w') as gz:
            writer = wrap_text_writer(gz, 'utf-8', manage=False)
            df.to_csv(writer, encoding='utf-8', mode='wb', index=False)
        f.seek(0)
        cnt = f.read()
    return Attachment(
        cnt, title=title, link_only=link_only, extension='.csv.gz'
    )