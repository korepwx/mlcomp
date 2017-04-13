# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from ..elements import CanvasJS
from ..components import dataframe_to_table
from sklearn.metrics import mean_absolute_error,mean_squared_error,explained_variance_score,r2_score

__all__ = [
    'time_series_regression_report'
]


def time_series_regression_report(truth, predict, timestamp, stddev=None, label=None,
                 log_likelihood=None, targets=None, per_target_summary=True,
                 name=None):

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
    kwargs = {}
    data.append({
        'name': 'truth',
        'showInLegend': True,
        'type': 'line',
        'color':TRUTH_LINE_COLOR,
        'dataPoints': [
            {'x': x*1000, 'y': y}
            for x, y in zip(df['timestamp'].values,df['truth'].values)
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
        print(stddev_values)
        for x, y in zip(df['timestamp'].values, stddev_values):
            print(x*1000,y)
        data.append({
            'name':'stddev',
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
def normalize_regression_report_args(truth, predict, label=None, targets=None,
                                     per_target=True):
    # check the arguments
    if predict.shape != truth.shape:
        raise TypeError('Shape of `predict` does not match `truth`.')
    if label is not None and len(label) != len(truth):
        raise TypeError('Size of `label` != size of `truth`.')

    # generate the target labels.
    if not per_target:
        targets = None
    else:
        if len(truth.shape) == 1:
            if targets is None:
                targets = ['0']
            else:
                if not isinstance(targets, np.ndarray):
                    targets = np.asarray(targets)
                if len(targets) != 1 or not isinstance(targets[0], str):
                    raise TypeError('Shape of `targets` does not match '
                                    '`truth`.')
        else:
            if targets is None:
                targets = []
                indices_it = (range(i) for i in truth.shape[1:])
                for indices in itertools.product(*indices_it):
                    targets.append('-'.join(str(s) for s in indices))
                targets = np.asarray(targets)
            else:
                if not isinstance(targets, np.ndarray):
                    targets = np.asarray(targets)
                if targets.shape != truth.shape[1:]:
                    raise TypeError('Shape of `targets` does not match '
                                    '`truth`.')
                targets = targets.reshape([-1])

    # flatten the dimensions in truth and target data to match the targets
    truth = truth.reshape([len(truth), -1])
    predict = predict.reshape([len(predict), -1])

    return truth, predict, label, targets

def regression_summary(truth, predict, label=None, targets=None,
                                 per_target_summary=True):
    def mkrow(y_true, y_pred):
        return np.asarray([
            mean_squared_error(y_true, y_pred),
            mean_absolute_error(y_true, y_pred),
            r2_score(y_true, y_pred, multioutput='uniform_average'),
            explained_variance_score(y_true, y_pred),
            len(y_true),
        ])

    columns = (
        'Mean Squared Error', 'Mean Absolute Error',
        'R2 Score', 'Explained Variance Score', '#Points'
    )

    truth, predict, label, targets = normalize_regression_report_args(
        truth, predict, label, targets, per_target_summary
    )

    # compose the data and the index
    data = []
    if targets is None:
        if label is None:
            data = [mkrow(truth, predict)]
            index = pd.Index(['total'])
        else:
            ulabels = list(unique_labels(label))
            for lbl in ulabels:
                mask = (label == lbl)
                data.append(mkrow(truth[mask], predict[mask]))
            data.append(mkrow(truth, predict))
            ulabels.append('total')
            index = pd.Index(ulabels, name='Label')
    else:
        if label is None:
            data = [mkrow(truth[:, i], predict[:, i])
                    for i in range(len(targets))]
            data.append(mkrow(truth, predict))
            index = pd.Index(list(targets) + ['total'], name='Target')
        else:
            target_index = []
            label_index = []
            for i in range(len(targets)):
                for lbl in list(unique_labels(label)):
                    mask = (label == lbl)
                    target_index.append(targets[i])
                    label_index.append(lbl)
                    data.append(mkrow(truth[mask][:, i], predict[mask][:, i]))
            target_index.append('')
            label_index.append('total')
            data.append(mkrow(truth, predict))
            index = pd.MultiIndex.from_tuples(
                [tuple(v) for v in zip(target_index, label_index)],
                names=['Target', 'Label']
            )

    summary = pd.DataFrame(data=data, columns=columns, index=index)
    return dataframe_to_table(summary, title='Regression Summary ')
