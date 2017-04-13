# -*- coding: utf-8 -*-
import six
import numpy as np

from ..elements import *

__all__ = [
    'loss_accuracy_curve',
]


def nan_to_none(v):
    return None if np.isnan(v) else v


def loss_accuracy_curve(metrics, metric_name='loss', secondary_metrics=None,
                        secondary_metric_name='accuracy', title=None,
                        step_name='step'):
    """"""
    data = []
    for name, (step, values) in six.iteritems(metrics):
        data.append({
            'name': name,
            'showInLegend': True,
            'type': 'line',
            'dataPoints': [
                {'x': x, 'y': nan_to_none(y)}
                for x, y in zip(step, values)
            ]
        })
    if secondary_metrics:
        for name, (step, values) in six.iteritems(secondary_metrics):
            data.append({
                'name': name,
                'showInLegend': True,
                'type': 'line',
                'dataPoints': [
                    {'x': x, 'y': nan_to_none(y)}
                    for x, y in zip(step, values)
                ],
                'axisYType': 'secondary',
            })

    chart = {
        'legend': {
            'horizontalAlign': 'center',
            'verticalAlign': 'top',
            'fontSize': 12
        },
        'zoomEnabled': True,
        'zoomType': 'xy',
        'axisX': {
            'title': step_name,
        },
        'axisY': {
            'title': metric_name,
        },
        'data': data
    }
    if secondary_metrics:
        chart['axisY2'] = {
            'title': secondary_metric_name,
        }
    if title:
        chart['title'] = {
            'text': title,
            'fontSize': 24,
        }
    return CanvasJS(chart)
