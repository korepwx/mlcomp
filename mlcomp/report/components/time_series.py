# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from ..elements import CanvasJS

__all__ = [
    'time_series_regression_curve'
]


def time_series_regression_curve(truth, predict, timestamp,
                                 stddev=None, label=None,
                                 log_likelihood=None):
    TRUTH_LINE_COLOR = '#aaa'
    PREDICT_LINE_COLOR = 'navy'
    STDDEV_RANGE_COLOR = 'rgba(0,0,255,0.2)'
    LIKELIHOOD_COLOR = 'orange'

    # re-arrange the data so that the timestamp are sorted
    ts_index = np.argsort(timestamp)
    ts = timestamp[ts_index]
    truth = truth[ts_index]
    predict = predict[ts_index]

    if label is not None:
        label = label[ts_index]
    if stddev is not None:
        stddev = stddev[ts_index]
    if log_likelihood is not None:
        log_likelihood = log_likelihood[ts_index]

    intervals = ts[1:] - ts[:-1]
    int_items, int_count = np.unique(intervals, return_counts=True)
    interval = int_items[np.argsort(-int_count)[0]]
    if np.any(int_items % interval > 0):
        raise ValueError('%s: non-homogeneous time intervals.' % ts)

    # split the data frame into continuous chunks, and fill the gap
    def fill_break(start_ts, end_ts):
        assert ((end_ts - start_ts) % interval == 0)
        gap_size = (end_ts - start_ts) // interval
        col_ts = np.arange(start_ts, end_ts, interval)
        col_ts = col_ts.astype(df['timestamp'].dtype)
        fill = {'timestamp': col_ts}
        for k in df:
            if k != 'timestamp':
                if k == 'label':
                    fill[k] = np.zeros(gap_size, dtype=np.int32)
                else:
                    fill[k] = np.full(gap_size, np.nan, dtype=df[k].dtype)
        return pd.DataFrame.from_dict(fill)

    buf = []
    breaks = np.where(ts[1:] - ts[:-1] > interval)[0] + np.asarray(1)
    last_pos = 0
    nan_count = 0

    df = pd.DataFrame(
        data={'timestamp': ts, 'truth': truth, 'predict': predict,
              'label': label, 'stddev': stddev, 'likelihood': log_likelihood}
    )
    for b in breaks:
        buf.append(df.iloc[last_pos: b])
        fill = fill_break(df['timestamp'].iloc[b - 1] + interval,
                          df['timestamp'].iloc[b])
        buf.append(fill)
        nan_count += len(fill)
        last_pos = b

    buf.append(df.iloc[last_pos:])

    # concatenate the chunks
    if len(buf) == 1:
        df = buf[0]
    else:
        df = pd.concat(buf, ignore_index=True)

    # generate the CanvasJS figure
    data = []
    data.append({
        'name': 'truth',
        'showInLegend': True,
        'type': 'line',
        'color': TRUTH_LINE_COLOR,
        'dataPoints': [
            {'x': x * 1000, 'y': y}
            for x, y in zip(df['timestamp'].values, df['truth'].values)
        ]
    })
    data.append({
        'name': 'predict',
        'showInLegend': True,
        'type': 'line',
        'color': PREDICT_LINE_COLOR,
        'dataPoints': [
            {'x': x * 1000, 'y': y}
            for x, y in zip(df['timestamp'].values, df['predict'].values)
        ]
    })

    if stddev is not None:
        stddev_values = (
            df['predict'].values.reshape([-1, 1]) +
            np.stack([-stddev, stddev], axis=1)
        )
        data.append({
            'name': 'stddev',
            'showInLegend': True,
            'type': 'rangeArea',
            'color': STDDEV_RANGE_COLOR,
            'dataPoints': [
                {'x': x * 1000, 'y': list(y)}
                for x, y in zip(df['timestamp'].values, stddev_values)
                ]
        })

    if log_likelihood is not None:
        likelihood_max = np.max(log_likelihood)
        likelihood_std = np.std(log_likelihood)
        likelihood_min = max(
            np.min(log_likelihood), likelihood_max - 4. * likelihood_std)
        likelihood_span = max(likelihood_max - likelihood_min, 1e-3)
        likelihood_max += likelihood_span * 0.05
        likelihood_min -= likelihood_span * 0.05
        data.append({
            'name': 'log-likelihood',
            'showInLegend': True,
            'type': 'line',
            'color': LIKELIHOOD_COLOR,
            'axisYType': 'secondary',
            'dataPoints': [
                {'x': x * 1000, 'y': y}
                for x, y in zip(df['timestamp'].values, log_likelihood)
            ]
        })

    chart = {
        'title': {
            'text': 'Regressin Truth and Predict Values',
        },
        'legend': {
            'horizontalAlign': 'center',
            'verticalAlign': 'top',
            'fontSize': 12
        },
        'zoomEnabled': True,
        'zoomType': 'xy',
        'axisX': {
            'title': 'Time',

        },
        'axisY': {
            'title': 'KPI',
            'includeZero': 'false',
        },
        'data': data
    }
    if log_likelihood is not None:
        chart['axisY2'] = {
            'title': 'log-likelihood',
        }

    return CanvasJS(data=chart)
