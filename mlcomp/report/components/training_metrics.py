# -*- coding: utf-8 -*-
import copy

from ..elements import *

__all__ = [
    'loss_accuracy_curve',
]


def loss_accuracy_curve(metrics, metric_name='loss', secondary_metrics=None,
                        secondary_metric_name='accuracy', step_name='step',
                        title=None):
    """Training loss and accuracy curve.
    
    This method generates a CanvasJS report object, which plots
    the training loss and accuracy curve.
    
    Parameters
    ----------
    metrics : collections.Iterable[dict]
        A list of dict, each representing a loss metric, with these entries:
        
            name : str
                The name of the loss metric.
                
            values : np.ndarray
                Loss metric at each step given by `steps`.
                
            steps : np.ndarray
                Number of each step.
                
            color : str
                Optional color of this metric (which can be any HTML color).
                
    metric_name : str
        Name of the main metrics. (default is 'loss')
        
    secondary_metrics : collections.Iterable[dict]
        List of the secondary metrics (with secondary y-axis at right).
        The secondary metrics are optionally.
        
    secondary_metric_name : str
        Name of the secondary metrics. (default is 'accuracy')
        
    step_name : str
        Name of the "steps", i.e., the x-axis. (default is 'step').
        
    title : str
        Title of the figure.
    """
    def add_metric(m, **kwargs):
        itm = copy.copy(kwargs)
        itm.update({
            'name': m['name'],
            'showInLegend': True,
            'type': 'line',
            'dataPoints': [
                {'x': x, 'y': y}
                for x, y in zip(m['steps'], m['values'])
            ]
        })
        if 'color' in m:
            itm['color'] = m['color']
        data.append(itm)

    data = []
    for metric in metrics:
        add_metric(metric)
    if secondary_metrics:
        for metric in secondary_metrics:
            add_metric(metric, axisYType='secondary')

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
