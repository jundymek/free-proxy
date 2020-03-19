import unittest
from unittest.mock import MagicMock

from fp.fp import FreeProxy


class TestProxy(unittest.TestCase):

    def test_empty_proxy_list(self):
        test = FreeProxy()
        test.get_proxy_list = MagicMock(return_value=[])
        self.assertEqual("There are no working proxies at this time.", test.get())

    def test_invalid_proxy(self):
        test = FreeProxy()
        test.get_proxy_list = MagicMock(return_value=['111.111.11:2222'])
        self.assertEqual("There are no working proxies at this time.", test.get())


if __name__ == '__main__':
    unittest.main()
