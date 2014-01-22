# -*- coding: utf-8 -*-
"""
    sqs.test_sqs
    ~~~~~~~~~~~~

    Test simple queue service.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import unittest


class SqsTest(unittest.TestCase):
    
    def setUp(self):
        self.client = None

    def test_get(self):
        pass

    def tearDown(self):
        self.client = None


if __name__ == "__main__":
    unittest.main()
