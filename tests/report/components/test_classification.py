#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import json
from io import StringIO, BytesIO

import pandas as pd
import numpy as np

from mlcomp.report import *


class ClassificationTestCase(unittest.TestCase):
    Y_TRUE = np.asarray(
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1,
         1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,
         0, 0, 0, 0, 0, 1]
    )
    Y_PROB = np.asarray(
        [0.2266932, 0.78086389, 0.30646888, 0.38332318, 0.10233496,
         0.52258974, 0.35135632, 0.23642456, 0.33524295, 0.25284156,
         0.27635788, 0.38670778, 0.88116806, 0.84260167, 0.41430036,
         0.26275521, 0.36336274, 0.87599771, 0.26607084, 0.3715676,
         0.37179117, 0.44046665, 0.33961926, 0.47571332, 0.08649715,
         0.23811064, 0.24923887, 0.73721014, 0.51468479, 0.32323209,
         0.92890874, 0.29001851, 0.19395192, 0.16987852, 0.41862858,
         0.16431411, 0.25713885, 0.07508522, 0.18788659, 0.62812246,
         0.59772088, 0.1285857, 0.47514496, 0.23362505, 0.552188,
         0.55056845, 0.16956083, 0.15835183, 0.32734213, 0.65417853]
    )
    Y_PRED = (Y_PROB >= 0.5).astype(np.int32)

    def test_binary_classification_auc_curve(self):
        r = binary_classification_auc_curve(
            y_true=self.Y_TRUE,
            y_prob=self.Y_PROB,
            title='Classification Precision-Recall'
        )
        r_payload = json.loads(r.data.data.decode('utf-8'))
        r_data = r_payload.pop('data')
        self.assertEqual(
            r_payload,
            {'title': {'fontSize': 24,
                       'text': 'Classification Precision-Recall'},
             'legend': {'horizontalAlign': 'center', 'verticalAlign': 'top',
                        'fontSize': 12},
             'axisX': {'title': 'Recall', 'minimum': 0, 'maximum': 1.05,
                       'gridColor': '#ccc', 'gridThickness': 1},
             'axisY': {'title': 'Precision', 'minimum': 0, 'maximum': 1.05,
                       'gridColor': '#ccc', 'gridThickness': 1}}
        )
        self.assertEqual(
            r_data[0]['name'],
            'AUC curve of class 0 (area=0.9307)'
        )
        self.assertEqual(
            r_data[1]['name'],
            'AUC curve of class 1 (area=0.8041)'
        )
        class_0_x = np.asarray([r['x'] for r in r_data[0]['dataPoints']])
        np.testing.assert_almost_equal(
            class_0_x,
            [1.0, 0.9705882352941176, 0.9411764705882353, 0.9117647058823529,
             0.8823529411764706, 0.8823529411764706, 0.8823529411764706,
             0.8529411764705882, 0.8529411764705882, 0.8235294117647058,
             0.8235294117647058, 0.7941176470588235, 0.7647058823529411,
             0.7352941176470589, 0.7352941176470589, 0.7058823529411765,
             0.7058823529411765, 0.7058823529411765, 0.6764705882352942,
             0.6470588235294118, 0.6176470588235294, 0.5882352941176471,
             0.5588235294117647, 0.5294117647058824, 0.5, 0.47058823529411764,
             0.4411764705882353, 0.4117647058823529, 0.38235294117647056,
             0.35294117647058826, 0.3235294117647059, 0.3235294117647059,
             0.29411764705882354, 0.2647058823529412, 0.23529411764705882,
             0.20588235294117646, 0.17647058823529413, 0.14705882352941177,
             0.11764705882352941, 0.08823529411764706, 0.058823529411764705,
             0.029411764705882353, 0.0]
        )
        class_0_y = np.asarray([r['y'] for r in r_data[0]['dataPoints']])
        np.testing.assert_almost_equal(
            class_0_y,
            [0.8095238095238095, 0.8048780487804879, 0.8, 0.7948717948717948,
             0.7894736842105263, 0.8108108108108109, 0.8333333333333334,
             0.8285714285714286, 0.8529411764705882, 0.8484848484848485, 0.875,
             0.8709677419354839, 0.8666666666666667, 0.8620689655172413,
             0.8928571428571429, 0.8888888888888888, 0.9230769230769231, 0.96,
             0.9583333333333334, 0.9565217391304348, 0.9545454545454546,
             0.9523809523809523, 0.95, 0.9473684210526315, 0.9444444444444444,
             0.9411764705882353, 0.9375, 0.9333333333333333, 0.9285714285714286,
             0.9230769230769231, 0.9166666666666666, 1.0, 1.0, 1.0, 1.0, 1.0,
             1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        )
        class_1_x = np.asarray([r['x'] for r in r_data[1]['dataPoints']])
        np.testing.assert_almost_equal(
            class_1_x,
            [1.0, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
             0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.875,
             0.8125, 0.8125, 0.75, 0.75, 0.75, 0.75, 0.6875, 0.6875, 0.625,
             0.625, 0.5625, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4375, 0.375, 0.3125,
             0.25, 0.1875, 0.125, 0.0625, 0.0]
        )
        class_1_y = np.asarray([r['y'] for r in r_data[1]['dataPoints']])
        np.testing.assert_almost_equal(
            class_1_y,
            [0.41025641025641024, 0.39473684210526316, 0.40540540540540543,
             0.4166666666666667, 0.42857142857142855, 0.4411764705882353,
             0.45454545454545453, 0.46875, 0.4838709677419355, 0.5,
             0.5172413793103449, 0.5357142857142857, 0.5555555555555556,
             0.5769230769230769, 0.6, 0.5833333333333334, 0.5652173913043478,
             0.5909090909090909, 0.5714285714285714, 0.6, 0.631578947368421,
             0.6666666666666666, 0.6470588235294118, 0.6875, 0.6666666666666666,
             0.7142857142857143, 0.6923076923076923, 0.6666666666666666,
             0.7272727272727273, 0.8, 0.8888888888888888, 1.0, 1.0, 1.0, 1.0,
             1.0, 1.0, 1.0, 1.0, 1.0]
        )

    def test_classification_summary(self):
        r = classification_summary(
            y_true=self.Y_TRUE,
            y_pred=self.Y_PRED,
            target_names=['class 0', 'class 1'],
            title='Classification Summary'
        )
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "Table", "footer": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": "total"}]}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "0.7728898"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "0.78"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "0.7732686"}]}, {"__id__": 10, "__type__": "TableCell", "children": [{"__id__": 11, "__type__": "Text", "text": "50"}]}]}], "header": [{"__id__": 12, "__type__": "TableRow", "cells": [{"__id__": 13, "__type__": "TableCell", "children": [{"__id__": 14, "__type__": "Text", "text": ""}], "colspan": 1}, {"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": "Precision"}]}, {"__id__": 17, "__type__": "TableCell", "children": [{"__id__": 18, "__type__": "Text", "text": "Recall"}]}, {"__id__": 19, "__type__": "TableCell", "children": [{"__id__": 20, "__type__": "Text", "text": "F1-Score"}]}, {"__id__": 21, "__type__": "TableCell", "children": [{"__id__": 22, "__type__": "Text", "text": "Support"}]}]}], "rows": [{"__id__": 23, "__type__": "TableRow", "cells": [{"__id__": 24, "__type__": "TableCell", "children": [{"__id__": 25, "__type__": "Text", "text": "class 0"}]}, {"__id__": 26, "__type__": "TableCell", "children": [{"__id__": 27, "__type__": "Text", "text": "0.8108108"}]}, {"__id__": 28, "__type__": "TableCell", "children": [{"__id__": 29, "__type__": "Text", "text": "0.8823529"}]}, {"__id__": 30, "__type__": "TableCell", "children": [{"__id__": 31, "__type__": "Text", "text": "0.8450704"}]}, {"__id__": 32, "__type__": "TableCell", "children": [{"__id__": 33, "__type__": "Text", "text": "34"}]}]}, {"__id__": 34, "__type__": "TableRow", "cells": [{"__id__": 35, "__type__": "TableCell", "children": [{"__id__": 36, "__type__": "Text", "text": "class 1"}]}, {"__id__": 37, "__type__": "TableCell", "children": [{"__id__": 38, "__type__": "Text", "text": "0.6923077"}]}, {"__id__": 39, "__type__": "TableCell", "children": [{"__id__": 40, "__type__": "Text", "text": "0.5625"}]}, {"__id__": 41, "__type__": "TableCell", "children": [{"__id__": 42, "__type__": "Text", "text": "0.6206897"}]}, {"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "16"}]}]}], "title": "Classification Summary"}'
        )

    def test_classification_result_attachment(self):
        r = classification_result_attachment(
            self.Y_TRUE, self.Y_PRED, self.Y_PROB,
            title='Classification Result'
        )
        with BytesIO(r.data) as f:
            data = json.loads(f.read().decode('utf-8'))
            y_true = np.asarray(data['y_true'])
            y_pred = np.asarray(data['y_pred'])
            y_prob = np.asarray(data['y_prob'])

        np.testing.assert_almost_equal(y_true, self.Y_TRUE)
        np.testing.assert_almost_equal(y_pred, self.Y_PRED)
        np.testing.assert_almost_equal(y_prob, self.Y_PROB)

if __name__ == '__main__':
    unittest.main()
