import unittest

import numpy as np

from mlcomp.utils import minibatch_iterator, minibatch_slices_iterator


class DataUtilsTestCase(unittest.TestCase):

    def test_minibatch_slices_iterator(self):
        self.assertEqual(
            list(minibatch_slices_iterator(0, 10, False)),
            []
        )
        self.assertEqual(
            list(minibatch_slices_iterator(9, 10, False)),
            [slice(0, 9, 1)]
        )
        self.assertEqual(
            list(minibatch_slices_iterator(10, 10, False)),
            [slice(0, 10, 1)]
        )
        self.assertEqual(
            list(minibatch_slices_iterator(10, 9, False)),
            [slice(0, 9, 1), slice(9, 10, 1)]
        )
        self.assertEqual(
            list(minibatch_slices_iterator(10, 9, True)),
            [slice(0, 9, 1)]
        )

    def test_minibatch_iterator(self):
        def assert_equal(x, y):
            self.assertEqual(len(x), len(y))
            for xx, yy in zip(x, y):
                np.testing.assert_equal(xx, yy)

        assert_equal(
            list(minibatch_iterator(np.arange(0), 10, False)),
            []
        )
        assert_equal(
            list(minibatch_iterator(np.arange(9), 10, False)),
            [np.arange(9)]
        )
        assert_equal(
            list(minibatch_iterator(np.arange(10), 10, False)),
            [np.arange(10)]
        )
        assert_equal(
            list(minibatch_iterator(np.arange(10), 9, False)),
            [np.arange(9), np.arange(9, 10)]
        )
        assert_equal(
            list(minibatch_iterator(np.arange(10), 9, True)),
            [np.arange(9)]
        )

    def test_split_numpy_array(self):
        # TODO: add tests for split_numpy_array
        pass


if __name__ == '__main__':
    unittest.main()
