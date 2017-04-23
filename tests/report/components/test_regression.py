# -*- coding: utf-8 -*-
import json
import unittest

import numpy as np

from mlcomp.report import *


class RegressionTestCase(unittest.TestCase):
    TRUTH = np.asarray(
        [[0.0, 1.0],
         [0.2486898871648548, 0.9685831611286311],
         [0.4817536741017153, 0.8763066800438636],
         [0.6845471059286887, 0.7289686274214116],
         [0.8443279255020151, 0.5358267949789967],
         [0.9510565162951535, 0.30901699437494745],
         [0.9980267284282716, 0.06279051952931329],
         [0.9822872507286886, -0.18738131458572482],
         [0.9048270524660195, -0.42577929156507277],
         [0.7705132427757893, -0.6374239897486896],
         [0.5877852522924732, -0.8090169943749473],
         [0.3681245526846777, -0.9297764858882515],
         [0.1253332335643041, -0.9921147013144779],
         [-0.1253332335643043, -0.9921147013144779],
         [-0.36812455268467836, -0.9297764858882512],
         [-0.5877852522924734, -0.8090169943749472],
         [-0.7705132427757894, -0.6374239897486896],
         [-0.9048270524660198, -0.42577929156507216],
         [-0.9822872507286887, -0.18738131458572463],
         [-0.9980267284282716, 0.06279051952931372],
         [-0.9510565162951536, 0.30901699437494723],
         [-0.8443279255020151, 0.5358267949789967],
         [-0.6845471059286883, 0.7289686274214119],
         [-0.4817536741017153, 0.8763066800438636],
         [-0.2486898871648545, 0.9685831611286312],
         [6.432490598706546e-16, 1.0],
         [0.2486898871648549, 0.9685831611286311],
         [0.4817536741017157, 0.8763066800438634],
         [0.6845471059286893, 0.7289686274214109],
         [0.8443279255020152, 0.5358267949789964],
         [0.9510565162951538, 0.3090169943749469],
         [0.9980267284282716, 0.06279051952931332],
         [0.9822872507286886, -0.18738131458572502],
         [0.9048270524660192, -0.42577929156507327],
         [0.7705132427757886, -0.6374239897486905],
         [0.5877852522924734, -0.8090169943749472],
         [0.368124552684678, -0.9297764858882513],
         [0.1253332335643039, -0.9921147013144779],
         [-0.12533323356430495, -0.9921147013144778],
         [-0.3681245526846789, -0.929776485888251],
         [-0.5877852522924728, -0.8090169943749477],
         [-0.7705132427757891, -0.6374239897486897],
         [-0.9048270524660197, -0.4257792915650724],
         [-0.9822872507286888, -0.187381314585724],
         [-0.9980267284282714, 0.06279051952931436],
         [-0.9510565162951532, 0.3090169943749487],
         [-0.8443279255020152, 0.5358267949789965],
         [-0.6845471059286885, 0.7289686274214118],
         [-0.4817536741017147, 0.8763066800438639],
         [-0.24868988716485388, 0.9685831611286313],
         [-4.898587196589413e-16, 1.0]]
    )
    LABEL = np.asarray(
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
         0, 1, 0, 0, 0, 0]
    )
    PREDICT = np.asarray(
        [[0.19073961607834158, 0.6130602925068296],
         [0.06180048844310332, 0.4844259614974147],
         [-0.29508463852512856, 0.8244933121514825],
         [0.5562847232640034, 1.5643292279968009],
         [0.841193759028724, 1.1528900157690862],
         [1.1054284079353844, 0.989827077490908],
         [1.0565333640002605, 0.9820160819115242],
         [0.9855865431652929, -1.08633971409754],
         [0.8623685266430159, 0.90113482101409],
         [0.45289370460945527, -0.5328297216833511],
         [0.5928137685168013, -2.312876079995772],
         [0.38580362570176935, -1.7144932664477421],
         [0.28110272700204086, 0.6530720559610205],
         [-0.34126280055577074, -0.3342191988704619],
         [-0.42723523243346057, -0.6546229334937423],
         [-0.7420056313952146, -0.1581738135542483],
         [-0.6799249428659663, 0.3680242103619139],
         [-0.8300929753142798, -1.5111763100953366],
         [-0.95994825048744, -0.07266617182526543],
         [-1.0716185000041643, -0.3530917936988599],
         [-0.9343041633218933, -0.18448090216898372],
         [-0.7535129999361787, 0.4339808718349253],
         [-0.665896870861998, -1.34806191004406],
         [-0.54376427057724, 1.0031068382212518],
         [1.0496607234419468, 0.8342432459271333],
         [0.8318359992704902, 1.0266597606800039],
         [0.47994156925617293, 1.9449897796641902],
         [0.44728219127043395, 0.5890606331081516],
         [0.7174616818670435, -0.7882674097980038],
         [0.8176668450837865, -0.5215244831232765],
         [0.9379540920753354, 3.6075830735826133],
         [0.8897216754790325, 1.4370149427807017],
         [1.0600557381536895, 0.5775359705894206],
         [0.8253489575239361, -0.8457353724001884],
         [0.9509806834461627, -0.6799629022384029],
         [0.5916136874596575, -0.32187977069135515],
         [0.33425018965955167, -1.0467008440941135],
         [0.1729476931128601, -1.496682569605788],
         [-0.08664304649722522, -1.0323918599443143],
         [-0.3373599440741263, -2.3999328417588717],
         [-0.5802269366525458, -0.26040617377376296],
         [-0.6959850494388243, -1.8165712505777651],
         [-0.7152836378530699, -0.4955620289769251],
         [-1.0228431398007665, 0.42051139925313724],
         [-1.9618016526224595, 0.09253381384826526],
         [-0.8060294494300088, -0.40366549724874945],
         [-2.381276112946783, 0.576707298211926],
         [-0.7335143724220312, 0.16220984362951474],
         [-0.4319358688721556, 0.3932797711447328],
         [-0.28751232261493215, 0.5719008703509652],
         [0.09380302829264438, 2.1126786791091297]]
    )

    def test_regression_summary(self):
        # test regression report with both targets and labels
        r = regression_summary(
            truth=self.TRUTH, predict=self.PREDICT,
            label=self.LABEL, per_target=True,
            target_names=['sin(x)', 'cos(x)']
        )
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "footer": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": "total"}], "colspan": 2}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "0.4985301"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "0.4381232"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "0.01622919"}]}, {"__id__": 10, "__type__": "TableCell", "children": [{"__id__": 11, "__type__": "Text", "text": "0.01676494"}]}, {"__id__": 12, "__type__": "TableCell", "children": [{"__id__": 13, "__type__": "Text", "text": "51"}]}]}], "header": [{"__id__": 14, "__type__": "TableRow", "cells": [{"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": ""}], "colspan": 2}, {"__id__": 17, "__type__": "TableCell", "children": [{"__id__": 18, "__type__": "Text", "text": "Squared Error"}]}, {"__id__": 19, "__type__": "TableCell", "children": [{"__id__": 20, "__type__": "Text", "text": "Absolute Error"}]}, {"__id__": 21, "__type__": "TableCell", "children": [{"__id__": 22, "__type__": "Text", "text": "R2 Score"}]}, {"__id__": 23, "__type__": "TableCell", "children": [{"__id__": 24, "__type__": "Text", "text": "Explained Variance"}]}, {"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "Support"}]}]}, {"__id__": 27, "__type__": "TableRow", "cells": [{"__id__": 28, "__type__": "TableCell", "children": [{"__id__": 29, "__type__": "Text", "text": "Target"}]}, {"__id__": 30, "__type__": "TableCell", "children": [{"__id__": 31, "__type__": "Text", "text": "Label"}]}, {"__id__": 32, "__type__": "TableCell", "children": [{"__id__": 33, "__type__": "Text", "text": ""}], "colspan": 5}]}], "rows": [{"__id__": 34, "__type__": "TableRow", "cells": [{"__id__": 35, "__type__": "TableCell", "children": [{"__id__": 36, "__type__": "Text", "text": "sin(x)"}], "rowspan": 2}, {"__id__": 37, "__type__": "TableCell", "children": [{"__id__": 38, "__type__": "Text", "text": "0"}]}, {"__id__": 39, "__type__": "TableCell", "children": [{"__id__": 40, "__type__": "Text", "text": "0.009430784"}]}, {"__id__": 41, "__type__": "TableCell", "children": [{"__id__": 42, "__type__": "Text", "text": "0.07398638"}]}, {"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "0.9807603"}]}, {"__id__": 45, "__type__": "TableCell", "children": [{"__id__": 46, "__type__": "Text", "text": "0.9810164"}]}, {"__id__": 47, "__type__": "TableCell", "children": [{"__id__": 48, "__type__": "Text", "text": "43"}]}]}, {"__id__": 49, "__type__": "TableRow", "cells": [{"__id__": 50, "__type__": "TableCell", "children": [{"__id__": 51, "__type__": "Text", "text": "1"}]}, {"__id__": 52, "__type__": "TableCell", "children": [{"__id__": 53, "__type__": "Text", "text": "0.8017391"}]}, {"__id__": 54, "__type__": "TableCell", "children": [{"__id__": 55, "__type__": "Text", "text": "0.7495812"}]}, {"__id__": 56, "__type__": "TableCell", "children": [{"__id__": 57, "__type__": "Text", "text": "-0.6882948"}]}, {"__id__": 58, "__type__": "TableCell", "children": [{"__id__": 59, "__type__": "Text", "text": "-0.6414097"}]}, {"__id__": 60, "__type__": "TableCell", "children": [{"__id__": 61, "__type__": "Text", "text": "8"}]}]}, {"__id__": 62, "__type__": "TableRow", "cells": [{"__id__": 63, "__type__": "TableCell", "children": [{"__id__": 64, "__type__": "Text", "text": "cos(x)"}], "rowspan": 2}, {"__id__": 65, "__type__": "TableCell", "children": [{"__id__": 66, "__type__": "Text", "text": "0"}]}, {"__id__": 67, "__type__": "TableCell", "children": [{"__id__": 68, "__type__": "Text", "text": "1.022872"}]}, {"__id__": 69, "__type__": "TableCell", "children": [{"__id__": 70, "__type__": "Text", "text": "0.8134438"}]}, {"__id__": 71, "__type__": "TableCell", "children": [{"__id__": 72, "__type__": "Text", "text": "-1.014304"}]}, {"__id__": 73, "__type__": "TableCell", "children": [{"__id__": 74, "__type__": "Text", "text": "-1.013077"}]}, {"__id__": 75, "__type__": "TableCell", "children": [{"__id__": 76, "__type__": "Text", "text": "43"}]}]}, {"__id__": 77, "__type__": "TableRow", "cells": [{"__id__": 78, "__type__": "TableCell", "children": [{"__id__": 79, "__type__": "Text", "text": "1"}]}, {"__id__": 80, "__type__": "TableCell", "children": [{"__id__": 81, "__type__": "Text", "text": "0.005890071"}]}, {"__id__": 82, "__type__": "TableCell", "children": [{"__id__": 83, "__type__": "Text", "text": "0.06655199"}]}, {"__id__": 84, "__type__": "TableCell", "children": [{"__id__": 85, "__type__": "Text", "text": "0.9851942"}]}, {"__id__": 86, "__type__": "TableCell", "children": [{"__id__": 87, "__type__": "Text", "text": "0.9858443"}]}, {"__id__": 88, "__type__": "TableCell", "children": [{"__id__": 89, "__type__": "Text", "text": "8"}]}]}]}
        )

        # test regression report with neither targets nor labels
        r = regression_summary(
            truth=self.TRUTH, predict=self.PREDICT,
            per_target=False
        )
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "header": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": ""}], "colspan": 1}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "Squared Error"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "Absolute Error"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "R2 Score"}]}, {"__id__": 10, "__type__": "TableCell", "children": [{"__id__": 11, "__type__": "Text", "text": "Explained Variance"}]}, {"__id__": 12, "__type__": "TableCell", "children": [{"__id__": 13, "__type__": "Text", "text": "Support"}]}]}], "rows": [{"__id__": 14, "__type__": "TableRow", "cells": [{"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": "total"}]}, {"__id__": 17, "__type__": "TableCell", "children": [{"__id__": 18, "__type__": "Text", "text": "0.4985301"}]}, {"__id__": 19, "__type__": "TableCell", "children": [{"__id__": 20, "__type__": "Text", "text": "0.4381232"}]}, {"__id__": 21, "__type__": "TableCell", "children": [{"__id__": 22, "__type__": "Text", "text": "0.01622919"}]}, {"__id__": 23, "__type__": "TableCell", "children": [{"__id__": 24, "__type__": "Text", "text": "0.01676494"}]}, {"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "51"}]}]}]}
        )

        # test regression report with only (unnamed) targets
        r = regression_summary(
            truth=self.TRUTH, predict=self.PREDICT,
            per_target=True
        )
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "footer": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": "total"}]}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "0.4985301"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "0.4381232"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "0.01622919"}]}, {"__id__": 10, "__type__": "TableCell", "children": [{"__id__": 11, "__type__": "Text", "text": "0.01676494"}]}, {"__id__": 12, "__type__": "TableCell", "children": [{"__id__": 13, "__type__": "Text", "text": "51"}]}]}], "header": [{"__id__": 14, "__type__": "TableRow", "cells": [{"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": ""}], "colspan": 1}, {"__id__": 17, "__type__": "TableCell", "children": [{"__id__": 18, "__type__": "Text", "text": "Squared Error"}]}, {"__id__": 19, "__type__": "TableCell", "children": [{"__id__": 20, "__type__": "Text", "text": "Absolute Error"}]}, {"__id__": 21, "__type__": "TableCell", "children": [{"__id__": 22, "__type__": "Text", "text": "R2 Score"}]}, {"__id__": 23, "__type__": "TableCell", "children": [{"__id__": 24, "__type__": "Text", "text": "Explained Variance"}]}, {"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "Support"}]}]}, {"__id__": 27, "__type__": "TableRow", "cells": [{"__id__": 28, "__type__": "TableCell", "children": [{"__id__": 29, "__type__": "Text", "text": "Target"}]}, {"__id__": 30, "__type__": "TableCell", "children": [{"__id__": 31, "__type__": "Text", "text": ""}], "colspan": 5}]}], "rows": [{"__id__": 32, "__type__": "TableRow", "cells": [{"__id__": 33, "__type__": "TableCell", "children": [{"__id__": 34, "__type__": "Text", "text": "[0]"}]}, {"__id__": 35, "__type__": "TableCell", "children": [{"__id__": 36, "__type__": "Text", "text": "0.1337144"}]}, {"__id__": 37, "__type__": "TableCell", "children": [{"__id__": 38, "__type__": "Text", "text": "0.179962"}]}, {"__id__": 39, "__type__": "TableCell", "children": [{"__id__": 40, "__type__": "Text", "text": "0.7272225"}]}, {"__id__": 41, "__type__": "TableCell", "children": [{"__id__": 42, "__type__": "Text", "text": "0.7276201"}]}, {"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "51"}]}]}, {"__id__": 45, "__type__": "TableRow", "cells": [{"__id__": 46, "__type__": "TableCell", "children": [{"__id__": 47, "__type__": "Text", "text": "[1]"}]}, {"__id__": 48, "__type__": "TableCell", "children": [{"__id__": 49, "__type__": "Text", "text": "0.8633458"}]}, {"__id__": 50, "__type__": "TableCell", "children": [{"__id__": 51, "__type__": "Text", "text": "0.6962843"}]}, {"__id__": 52, "__type__": "TableCell", "children": [{"__id__": 53, "__type__": "Text", "text": "-0.6947642"}]}, {"__id__": 54, "__type__": "TableCell", "children": [{"__id__": 55, "__type__": "Text", "text": "-0.6940902"}]}, {"__id__": 56, "__type__": "TableCell", "children": [{"__id__": 57, "__type__": "Text", "text": "51"}]}]}]}
        )

        # test regression report with only label
        r = regression_summary(
            truth=self.TRUTH, predict=self.PREDICT, label=self.LABEL,
            per_target=False,
        )
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "footer": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": "total"}]}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "0.4985301"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "0.4381232"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "0.01622919"}]}, {"__id__": 10, "__type__": "TableCell", "children": [{"__id__": 11, "__type__": "Text", "text": "0.01676494"}]}, {"__id__": 12, "__type__": "TableCell", "children": [{"__id__": 13, "__type__": "Text", "text": "51"}]}]}], "header": [{"__id__": 14, "__type__": "TableRow", "cells": [{"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": ""}], "colspan": 1}, {"__id__": 17, "__type__": "TableCell", "children": [{"__id__": 18, "__type__": "Text", "text": "Squared Error"}]}, {"__id__": 19, "__type__": "TableCell", "children": [{"__id__": 20, "__type__": "Text", "text": "Absolute Error"}]}, {"__id__": 21, "__type__": "TableCell", "children": [{"__id__": 22, "__type__": "Text", "text": "R2 Score"}]}, {"__id__": 23, "__type__": "TableCell", "children": [{"__id__": 24, "__type__": "Text", "text": "Explained Variance"}]}, {"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "Support"}]}]}, {"__id__": 27, "__type__": "TableRow", "cells": [{"__id__": 28, "__type__": "TableCell", "children": [{"__id__": 29, "__type__": "Text", "text": "Label"}]}, {"__id__": 30, "__type__": "TableCell", "children": [{"__id__": 31, "__type__": "Text", "text": ""}], "colspan": 5}]}], "rows": [{"__id__": 32, "__type__": "TableRow", "cells": [{"__id__": 33, "__type__": "TableCell", "children": [{"__id__": 34, "__type__": "Text", "text": "0"}]}, {"__id__": 35, "__type__": "TableCell", "children": [{"__id__": 36, "__type__": "Text", "text": "0.5161516"}]}, {"__id__": 37, "__type__": "TableCell", "children": [{"__id__": 38, "__type__": "Text", "text": "0.4437151"}]}, {"__id__": 39, "__type__": "TableCell", "children": [{"__id__": 40, "__type__": "Text", "text": "-0.016772"}]}, {"__id__": 41, "__type__": "TableCell", "children": [{"__id__": 42, "__type__": "Text", "text": "-0.01603017"}]}, {"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "43"}]}]}, {"__id__": 45, "__type__": "TableRow", "cells": [{"__id__": 46, "__type__": "TableCell", "children": [{"__id__": 47, "__type__": "Text", "text": "1"}]}, {"__id__": 48, "__type__": "TableCell", "children": [{"__id__": 49, "__type__": "Text", "text": "0.4038146"}]}, {"__id__": 50, "__type__": "TableCell", "children": [{"__id__": 51, "__type__": "Text", "text": "0.4080666"}]}, {"__id__": 52, "__type__": "TableCell", "children": [{"__id__": 53, "__type__": "Text", "text": "0.1484497"}]}, {"__id__": 54, "__type__": "TableCell", "children": [{"__id__": 55, "__type__": "Text", "text": "0.1722173"}]}, {"__id__": 56, "__type__": "TableCell", "children": [{"__id__": 57, "__type__": "Text", "text": "8"}]}]}]}
        )


if __name__ == '__main__':
    unittest.main()
