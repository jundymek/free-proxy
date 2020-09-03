import unittest
from unittest.mock import MagicMock

from fp.fp import FreeProxy


class TestProxy(unittest.TestCase):

    def test_empty_proxy_list(self):
        test = FreeProxy()
        test.get_proxy_list = MagicMock(return_value=[])
        self.assertEqual(
            "There are no working proxies at this time.", test.get())

    def test_invalid_proxy(self):
        test = FreeProxy()
        test.get_proxy_list = MagicMock(return_value=['111.111.11:2222'])
        self.assertEqual(
            "There are no working proxies at this time.", test.get())

    def test_anonym_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list())
        test2 = FreeProxy(anonym=True)
        cnt2 = len(test2.get_proxy_list())
        self.assertTrue(cnt2 < cnt1)


if __name__ == '__main__':
    unittest.main()
