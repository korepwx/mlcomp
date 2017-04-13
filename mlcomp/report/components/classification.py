# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from collections import OrderedDict
from sklearn.metrics import average_precision_score, precision_recall_curve,precision_recall_fscore_support
from ..elements import CanvasJS,Table,TableRow,Text
from sklearn.utils.multiclass import unique_labels
from ..components import dataframe_to_table

__all__ = [
    'classification_report'
]

def classification_report(truth, predict, proba, title=None):
    """Create a classification report.
    Parameters
    ----------
    truth : numpy.ndarray
        Ground truth (correct) target values.

    predict : numpy.ndarray
        Estimated target as returned by the classifier.

    proba : numpy.ndarray
        Estimated probabilities for each target to be each class.

    title : str
        title of this report.
    """

    p0, r0, th = precision_recall_curve(truth, proba)
    area0 = average_precision_score(truth, proba)
    a, b = 1 - truth, 1.0 - proba
    p1, r1, th = precision_recall_curve(a, b)
    area1 = average_precision_score(a, b)

    classification_data = {
        'title': {
            'text': 'Precision-Recall Curve of Binary Classification',
        },
        'legend': {
            'horizontalAlign': 'center',
            'verticalAlign': 'top',
            'fontSize': 12,
            'maxWidth': 400,
        },
        'axisX': {
            'title': "Recall",
            'minimum': 0,
            'maximum': 1,
            'gridColor': "gray",
            'gridThickness': 1,
        },
        'axisY': {
            'title': "Precision",
            'minimum': 0,
            'maximum': 1,
            'gridColor': "gray",
            'gridThickness': 1,
        },
        'data': [{
            'name':'Precision-Recall curve of class 0 (area=%.4f)' % area0,
            'showInLegend': True,
            'type': 'line',
            'dataPoints': [
                {'x': x, 'y': y} for x,y in zip(r0,p0)
            ]
        },
            {
                'name':'Precision-Recall curve of class 1 (area=%.4f)' % area1,
                'showInLegend': True,
                'type': 'line',
                'dataPoints': [
                    {'x': x, 'y': y} for x, y in zip(r1, p1)
                ]
            }]
    }

    return CanvasJS(data=classification_data)

def classfication_summary(y_true, y_pred, labels=None,
                                    target_names=None):

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
    return dataframe_to_table(summary, title='Classification Summary ')
