# -*- coding: utf-8 -*-
import json
import unittest

import numpy as np

from mlcomp.report import loss_accuracy_curve


class TrainingMetricsTestCase(unittest.TestCase):

    def test_loss_accuracy_curve(self):
        # generate the test payload
        steps = np.arange(101)
        loss = np.exp(-steps * 0.1) * 20. + np.random.normal(size=101) * 2.
        loss = loss - np.min(loss) + .2
        valid_steps = np.arange(0, 101, 10)
        valid_loss = (np.exp(-valid_steps * 0.1) * 25. +
                      np.random.normal(size=11) * 0.5)
        valid_loss = valid_loss - np.min(valid_loss)
        valid_acc = np.exp(-valid_loss * 0.1)

        # get a report with both metrics
        r = loss_accuracy_curve(
            metrics=[
                {'name': 'loss', 'steps': steps,
                 'values': loss, 'color': 'navy'},
                {'name': 'valid loss', 'steps': valid_steps,
                 'values': valid_loss, 'color': 'orangered'},
            ],
            metric_name='the loss',
            secondary_metrics=[
                {'name': 'valid acc', 'steps': valid_steps,
                 'values': valid_acc, 'color': 'green'},
            ],
            secondary_metric_name='the accuracy',
            step_name='the step',
            title='Training Metrics'
        )
        r_payload = json.loads(r.data.data.decode('utf-8'))
        r_data = r_payload.pop('data')
        self.assertEqual(
            r_payload,
            {'legend': {'horizontalAlign': 'center', 'verticalAlign': 'top',
                        'fontSize': 12},
             'zoomEnabled': True,
             'zoomType': 'xy',
             'axisX': {'title': 'the step'},
             'axisY2': {'title': 'the accuracy'},
             'title': {'text': 'Training Metrics', 'fontSize': 24},
             'axisY': {'title': 'the loss'}}
        )
        self.assertEqual(len(r_data), 3)

        for i, (name, steps_, values, color, secondary) in enumerate([
                    ('loss', steps, loss, 'navy', False),
                    ('valid loss', valid_steps, valid_loss, 'orangered', False),
                    ('valid acc', valid_steps, valid_acc, 'green', True)
                ]):
            r_payload_i = r_data[i]
            r_data_i = r_payload_i.pop('dataPoints')

            r_payload_i_truth = {
                'showInLegend': True, 'color': color, 'type': 'line',
                'name': name
            }
            if secondary:
                r_payload_i_truth['axisYType'] = 'secondary'
            self.assertEqual(r_payload_i, r_payload_i_truth)
            np.testing.assert_almost_equal(
                np.asarray([r['x'] for r in r_data_i]), steps_)
            np.testing.assert_almost_equal(
                np.asarray([r['y'] for r in r_data_i]), values)

        # get a report of only one metric
        r = loss_accuracy_curve(
            metrics=[
                {'name': 'loss', 'steps': steps,
                 'values': loss, 'color': 'navy'}
            ]
        )
        r_payload = json.loads(r.data.data.decode('utf-8'))
        r_data = r_payload.pop('data')
        self.assertEqual(
            r_payload,
            {'legend': {'horizontalAlign': 'center', 'verticalAlign': 'top',
                        'fontSize': 12},
             'zoomEnabled': True,
             'zoomType': 'xy',
             'axisX': {'title': 'step'},
             'axisY': {'title': 'loss'}}
        )
        self.assertEqual(len(r_data), 1)
        r_payload = r_data[0]
        r_data = r_payload.pop('dataPoints')
        self.assertEqual(
            r_payload,
            {'showInLegend': True, 'color': 'navy', 'type': 'line',
             'name': 'loss'}
        )
        np.testing.assert_almost_equal(
            np.asarray([r['x'] for r in r_data]), steps)
        np.testing.assert_almost_equal(
            np.asarray([r['y'] for r in r_data]), loss)

if __name__ == '__main__':
    unittest.main()

