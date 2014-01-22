# -*- coding: utf-8 -*-
"""
    sqs.test_client
    ~~~~~~~~~~~~~~~

    Test Kestrel client.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import unittest


class ClientTest(unittest.TestCase):
    
    def setUp(self):
        self.client = Kestrel()
        self.client.flush_all()

    def test_get(self):
        pass

    def tearDown(self):
        self.client.close()
        self.client = None


if __name__ == "__main__":
    unittest.main()
