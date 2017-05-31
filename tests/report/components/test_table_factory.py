# -*- coding: utf-8 -*-
import json
import unittest

import numpy as np
import pandas as pd

from mlcomp.report import data_frame_to_table


class TableFactoryTestCase(unittest.TestCase):

    def test_data_frame_to_table(self):
        # test single index table with unnamed index
        r = data_frame_to_table(pd.DataFrame(
            {'AAA': [4, 5, 6, 7], 'BBB': [10, 20, 30, 40],
             'CCC': [100, 50, -30, -50]}
        ))
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "header": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": ""}], "colspan": 1}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "AAA"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "BBB"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "CCC"}]}]}], "rows": [{"__id__": 10, "__type__": "TableRow", "cells": [{"__id__": 11, "__type__": "TableCell", "children": [{"__id__": 12, "__type__": "Text", "text": "0"}]}, {"__id__": 13, "__type__": "TableCell", "children": [{"__id__": 14, "__type__": "Text", "text": "4"}]}, {"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": "10"}]}, {"__id__": 17, "__type__": "TableCell", "children": [{"__id__": 18, "__type__": "Text", "text": "100"}]}]}, {"__id__": 19, "__type__": "TableRow", "cells": [{"__id__": 20, "__type__": "TableCell", "children": [{"__id__": 21, "__type__": "Text", "text": "1"}]}, {"__id__": 22, "__type__": "TableCell", "children": [{"__id__": 23, "__type__": "Text", "text": "5"}]}, {"__id__": 24, "__type__": "TableCell", "children": [{"__id__": 25, "__type__": "Text", "text": "20"}]}, {"__id__": 26, "__type__": "TableCell", "children": [{"__id__": 27, "__type__": "Text", "text": "50"}]}]}, {"__id__": 28, "__type__": "TableRow", "cells": [{"__id__": 29, "__type__": "TableCell", "children": [{"__id__": 30, "__type__": "Text", "text": "2"}]}, {"__id__": 31, "__type__": "TableCell", "children": [{"__id__": 32, "__type__": "Text", "text": "6"}]}, {"__id__": 33, "__type__": "TableCell", "children": [{"__id__": 34, "__type__": "Text", "text": "30"}]}, {"__id__": 35, "__type__": "TableCell", "children": [{"__id__": 36, "__type__": "Text", "text": "-30"}]}]}, {"__id__": 37, "__type__": "TableRow", "cells": [{"__id__": 38, "__type__": "TableCell", "children": [{"__id__": 39, "__type__": "Text", "text": "3"}]}, {"__id__": 40, "__type__": "TableCell", "children": [{"__id__": 41, "__type__": "Text", "text": "7"}]}, {"__id__": 42, "__type__": "TableCell", "children": [{"__id__": 43, "__type__": "Text", "text": "40"}]}, {"__id__": 44, "__type__": "TableCell", "children": [{"__id__": 45, "__type__": "Text", "text": "-50"}]}]}]}
        )

        # test single index table with named index
        r = data_frame_to_table(pd.DataFrame(
            {'AAA': [4, 5, 6, 7], 'BBB': [10, 20, 30, 40],
             'CCC': [100, 50, -30, -50]},
            index=pd.Index([0, 1, 2, 3], name='my-index')
        ))
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "header": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": ""}], "colspan": 1}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "AAA"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "BBB"}]}, {"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "text": "CCC"}]}]}, {"__id__": 10, "__type__": "TableRow", "cells": [{"__id__": 11, "__type__": "TableCell", "children": [{"__id__": 12, "__type__": "Text", "text": "my-index"}]}, {"__id__": 13, "__type__": "TableCell", "children": [{"__id__": 14, "__type__": "Text", "text": ""}], "colspan": 3}]}], "rows": [{"__id__": 15, "__type__": "TableRow", "cells": [{"__id__": 16, "__type__": "TableCell", "children": [{"__id__": 17, "__type__": "Text", "text": "0"}]}, {"__id__": 18, "__type__": "TableCell", "children": [{"__id__": 19, "__type__": "Text", "text": "4"}]}, {"__id__": 20, "__type__": "TableCell", "children": [{"__id__": 21, "__type__": "Text", "text": "10"}]}, {"__id__": 22, "__type__": "TableCell", "children": [{"__id__": 23, "__type__": "Text", "text": "100"}]}]}, {"__id__": 24, "__type__": "TableRow", "cells": [{"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "1"}]}, {"__id__": 27, "__type__": "TableCell", "children": [{"__id__": 28, "__type__": "Text", "text": "5"}]}, {"__id__": 29, "__type__": "TableCell", "children": [{"__id__": 30, "__type__": "Text", "text": "20"}]}, {"__id__": 31, "__type__": "TableCell", "children": [{"__id__": 32, "__type__": "Text", "text": "50"}]}]}, {"__id__": 33, "__type__": "TableRow", "cells": [{"__id__": 34, "__type__": "TableCell", "children": [{"__id__": 35, "__type__": "Text", "text": "2"}]}, {"__id__": 36, "__type__": "TableCell", "children": [{"__id__": 37, "__type__": "Text", "text": "6"}]}, {"__id__": 38, "__type__": "TableCell", "children": [{"__id__": 39, "__type__": "Text", "text": "30"}]}, {"__id__": 40, "__type__": "TableCell", "children": [{"__id__": 41, "__type__": "Text", "text": "-30"}]}]}, {"__id__": 42, "__type__": "TableRow", "cells": [{"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "3"}]}, {"__id__": 45, "__type__": "TableCell", "children": [{"__id__": 46, "__type__": "Text", "text": "7"}]}, {"__id__": 47, "__type__": "TableCell", "children": [{"__id__": 48, "__type__": "Text", "text": "40"}]}, {"__id__": 49, "__type__": "TableCell", "children": [{"__id__": 50, "__type__": "Text", "text": "-50"}]}]}]}
        )

        # test multi-index table with unnamed index
        arrays = [
            ['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
            ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']
        ]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples)
        df = pd.DataFrame(
            np.arange(16).reshape([8, 2]), index=index, columns=['A', 'B'])
        r = data_frame_to_table(df)
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "header": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": ""}], "colspan": 2}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "A"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "B"}]}]}], "rows": [{"__id__": 8, "__type__": "TableRow", "cells": [{"__id__": 9, "__type__": "TableCell", "children": [{"__id__": 10, "__type__": "Text", "text": "bar"}], "rowspan": 2}, {"__id__": 11, "__type__": "TableCell", "children": [{"__id__": 12, "__type__": "Text", "text": "one"}]}, {"__id__": 13, "__type__": "TableCell", "children": [{"__id__": 14, "__type__": "Text", "text": "0"}]}, {"__id__": 15, "__type__": "TableCell", "children": [{"__id__": 16, "__type__": "Text", "text": "1"}]}]}, {"__id__": 17, "__type__": "TableRow", "cells": [{"__id__": 18, "__type__": "TableCell", "children": [{"__id__": 19, "__type__": "Text", "text": "two"}]}, {"__id__": 20, "__type__": "TableCell", "children": [{"__id__": 21, "__type__": "Text", "text": "2"}]}, {"__id__": 22, "__type__": "TableCell", "children": [{"__id__": 23, "__type__": "Text", "text": "3"}]}]}, {"__id__": 24, "__type__": "TableRow", "cells": [{"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "baz"}], "rowspan": 2}, {"__id__": 27, "__type__": "TableCell", "children": [{"__id__": 28, "__type__": "Text", "text": "one"}]}, {"__id__": 29, "__type__": "TableCell", "children": [{"__id__": 30, "__type__": "Text", "text": "4"}]}, {"__id__": 31, "__type__": "TableCell", "children": [{"__id__": 32, "__type__": "Text", "text": "5"}]}]}, {"__id__": 33, "__type__": "TableRow", "cells": [{"__id__": 34, "__type__": "TableCell", "children": [{"__id__": 35, "__type__": "Text", "text": "two"}]}, {"__id__": 36, "__type__": "TableCell", "children": [{"__id__": 37, "__type__": "Text", "text": "6"}]}, {"__id__": 38, "__type__": "TableCell", "children": [{"__id__": 39, "__type__": "Text", "text": "7"}]}]}, {"__id__": 40, "__type__": "TableRow", "cells": [{"__id__": 41, "__type__": "TableCell", "children": [{"__id__": 42, "__type__": "Text", "text": "foo"}], "rowspan": 2}, {"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "one"}]}, {"__id__": 45, "__type__": "TableCell", "children": [{"__id__": 46, "__type__": "Text", "text": "8"}]}, {"__id__": 47, "__type__": "TableCell", "children": [{"__id__": 48, "__type__": "Text", "text": "9"}]}]}, {"__id__": 49, "__type__": "TableRow", "cells": [{"__id__": 50, "__type__": "TableCell", "children": [{"__id__": 51, "__type__": "Text", "text": "two"}]}, {"__id__": 52, "__type__": "TableCell", "children": [{"__id__": 53, "__type__": "Text", "text": "10"}]}, {"__id__": 54, "__type__": "TableCell", "children": [{"__id__": 55, "__type__": "Text", "text": "11"}]}]}, {"__id__": 56, "__type__": "TableRow", "cells": [{"__id__": 57, "__type__": "TableCell", "children": [{"__id__": 58, "__type__": "Text", "text": "qux"}], "rowspan": 2}, {"__id__": 59, "__type__": "TableCell", "children": [{"__id__": 60, "__type__": "Text", "text": "one"}]}, {"__id__": 61, "__type__": "TableCell", "children": [{"__id__": 62, "__type__": "Text", "text": "12"}]}, {"__id__": 63, "__type__": "TableCell", "children": [{"__id__": 64, "__type__": "Text", "text": "13"}]}]}, {"__id__": 65, "__type__": "TableRow", "cells": [{"__id__": 66, "__type__": "TableCell", "children": [{"__id__": 67, "__type__": "Text", "text": "two"}]}, {"__id__": 68, "__type__": "TableCell", "children": [{"__id__": 69, "__type__": "Text", "text": "14"}]}, {"__id__": 70, "__type__": "TableCell", "children": [{"__id__": 71, "__type__": "Text", "text": "15"}]}]}]}
        )

        # test multi-index with named index
        index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
        df = pd.DataFrame(
            np.arange(16).reshape([8, 2]), index=index, columns=['A', 'B'])
        r = data_frame_to_table(df, title='My Table', name='the-table')
        self.assertEqual(
            json.loads(r.to_json(sort_keys=True)),
            {"__id__": 0, "__type__": "Table", "header": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": ""}], "colspan": 2}, {"__id__": 4, "__type__": "TableCell", "children": [{"__id__": 5, "__type__": "Text", "text": "A"}]}, {"__id__": 6, "__type__": "TableCell", "children": [{"__id__": 7, "__type__": "Text", "text": "B"}]}]}, {"__id__": 8, "__type__": "TableRow", "cells": [{"__id__": 9, "__type__": "TableCell", "children": [{"__id__": 10, "__type__": "Text", "text": "first"}]}, {"__id__": 11, "__type__": "TableCell", "children": [{"__id__": 12, "__type__": "Text", "text": "second"}]}, {"__id__": 13, "__type__": "TableCell", "children": [{"__id__": 14, "__type__": "Text", "text": ""}], "colspan": 2}]}], "name": "the-table", "rows": [{"__id__": 15, "__type__": "TableRow", "cells": [{"__id__": 16, "__type__": "TableCell", "children": [{"__id__": 17, "__type__": "Text", "text": "bar"}], "rowspan": 2}, {"__id__": 18, "__type__": "TableCell", "children": [{"__id__": 19, "__type__": "Text", "text": "one"}]}, {"__id__": 20, "__type__": "TableCell", "children": [{"__id__": 21, "__type__": "Text", "text": "0"}]}, {"__id__": 22, "__type__": "TableCell", "children": [{"__id__": 23, "__type__": "Text", "text": "1"}]}]}, {"__id__": 24, "__type__": "TableRow", "cells": [{"__id__": 25, "__type__": "TableCell", "children": [{"__id__": 26, "__type__": "Text", "text": "two"}]}, {"__id__": 27, "__type__": "TableCell", "children": [{"__id__": 28, "__type__": "Text", "text": "2"}]}, {"__id__": 29, "__type__": "TableCell", "children": [{"__id__": 30, "__type__": "Text", "text": "3"}]}]}, {"__id__": 31, "__type__": "TableRow", "cells": [{"__id__": 32, "__type__": "TableCell", "children": [{"__id__": 33, "__type__": "Text", "text": "baz"}], "rowspan": 2}, {"__id__": 34, "__type__": "TableCell", "children": [{"__id__": 35, "__type__": "Text", "text": "one"}]}, {"__id__": 36, "__type__": "TableCell", "children": [{"__id__": 37, "__type__": "Text", "text": "4"}]}, {"__id__": 38, "__type__": "TableCell", "children": [{"__id__": 39, "__type__": "Text", "text": "5"}]}]}, {"__id__": 40, "__type__": "TableRow", "cells": [{"__id__": 41, "__type__": "TableCell", "children": [{"__id__": 42, "__type__": "Text", "text": "two"}]}, {"__id__": 43, "__type__": "TableCell", "children": [{"__id__": 44, "__type__": "Text", "text": "6"}]}, {"__id__": 45, "__type__": "TableCell", "children": [{"__id__": 46, "__type__": "Text", "text": "7"}]}]}, {"__id__": 47, "__type__": "TableRow", "cells": [{"__id__": 48, "__type__": "TableCell", "children": [{"__id__": 49, "__type__": "Text", "text": "foo"}], "rowspan": 2}, {"__id__": 50, "__type__": "TableCell", "children": [{"__id__": 51, "__type__": "Text", "text": "one"}]}, {"__id__": 52, "__type__": "TableCell", "children": [{"__id__": 53, "__type__": "Text", "text": "8"}]}, {"__id__": 54, "__type__": "TableCell", "children": [{"__id__": 55, "__type__": "Text", "text": "9"}]}]}, {"__id__": 56, "__type__": "TableRow", "cells": [{"__id__": 57, "__type__": "TableCell", "children": [{"__id__": 58, "__type__": "Text", "text": "two"}]}, {"__id__": 59, "__type__": "TableCell", "children": [{"__id__": 60, "__type__": "Text", "text": "10"}]}, {"__id__": 61, "__type__": "TableCell", "children": [{"__id__": 62, "__type__": "Text", "text": "11"}]}]}, {"__id__": 63, "__type__": "TableRow", "cells": [{"__id__": 64, "__type__": "TableCell", "children": [{"__id__": 65, "__type__": "Text", "text": "qux"}], "rowspan": 2}, {"__id__": 66, "__type__": "TableCell", "children": [{"__id__": 67, "__type__": "Text", "text": "one"}]}, {"__id__": 68, "__type__": "TableCell", "children": [{"__id__": 69, "__type__": "Text", "text": "12"}]}, {"__id__": 70, "__type__": "TableCell", "children": [{"__id__": 71, "__type__": "Text", "text": "13"}]}]}, {"__id__": 72, "__type__": "TableRow", "cells": [{"__id__": 73, "__type__": "TableCell", "children": [{"__id__": 74, "__type__": "Text", "text": "two"}]}, {"__id__": 75, "__type__": "TableCell", "children": [{"__id__": 76, "__type__": "Text", "text": "14"}]}, {"__id__": 77, "__type__": "TableCell", "children": [{"__id__": 78, "__type__": "Text", "text": "15"}]}]}], "title": "My Table"}
        )


if __name__ == '__main__':
    unittest.main()
