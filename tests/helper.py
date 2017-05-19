# -*- coding: utf-8 -*-
import unittest

__all__ = ['TestCase']


class TestCase(unittest.TestCase):
    """Extended TestCase class."""


if not hasattr(TestCase, 'assertRaisesRegex'):
    TestCase.assertRaisesRegex = TestCase.assertRaisesRegexp
