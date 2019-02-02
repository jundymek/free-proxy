import unittest
import io
import sys
from unittest.mock import MagicMock

from free_proxy import FreeProxy


class TestProxy(unittest.TestCase):

    def test_empty_proxy_list(self):
        # captured_output = io.StringIO()  # Create StringIO object
        # sys.stdout = captured_output
        thing = FreeProxy()
        thing.get_proxy_list = MagicMock(return_value=[])
        thing.get()
        self.assertEqual(None, thing.get())

    def test_invalid_proxy(self):
        thing = FreeProxy()
        thing.get_proxy_list = MagicMock(return_value=['111.111.11:2222'])
        self.assertEqual(None, thing.get())
