import unittest
from unittest.mock import MagicMock

import lxml.html as lh

from fp.errors import FreeProxyException
from fp.fp import FreeProxy


class TestProxy(unittest.TestCase):

    def test_empty_proxy_list(self):
        test = FreeProxy()
        test.get_proxy_list = MagicMock(return_value=[])
        self.assertRaisesRegex(
            FreeProxyException, 'There are no working proxies at this time.', test.get)

    def test_invalid_proxy(self):
        test = FreeProxy()
        test.get_proxy_list = MagicMock(return_value=['111.111.11:2222'])
        self.assertRaisesRegex(
            FreeProxyException, 'There are no working proxies at this time.', test.get)

    def test_anonym_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list())
        test2 = FreeProxy(anonym=True)
        cnt2 = len(test2.get_proxy_list())
        self.assertTrue(cnt2 < cnt1)

    def test_elite_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list())
        test2 = FreeProxy(elite=True)
        cnt2 = len(test2.get_proxy_list())
        self.assertTrue(cnt2 < cnt1)

    def test_google_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list())
        test2 = FreeProxy(google=True)
        test3 = FreeProxy(google=False)
        cnt2 = len(test2.get_proxy_list())
        cnt3 = len(test3.get_proxy_list())
        self.assertTrue(cnt2 < cnt1)
        self.assertTrue(cnt3 < cnt1)

    def test_criteria_defaults(self):
        '''Default settings: anonym = False, elite = False, google = None'''
        subject = FreeProxy()
        actual_0 = subject._FreeProxy__criteria(self.__tr_elements()[0])
        actual_1 = subject._FreeProxy__criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(True, actual_1)

    def test_criteria_anonym_true(self):
        subject = FreeProxy(anonym=True)
        actual_0 = subject._FreeProxy__criteria(self.__tr_elements()[0])
        actual_1 = subject._FreeProxy__criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(False, actual_1)

    def test_criteria_elite_true(self):
        subject = FreeProxy(elite=True)
        actual_0 = subject._FreeProxy__criteria(self.__tr_elements()[0])
        actual_1 = subject._FreeProxy__criteria(self.__tr_elements()[1])
        self.assertEqual(False, actual_0)
        self.assertEqual(True, actual_1)

    def test_criteria_google_false(self):
        subject = FreeProxy(google=False)
        actual_0 = subject._FreeProxy__criteria(self.__tr_elements()[0])
        actual_1 = subject._FreeProxy__criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(False, actual_1)

    def test_criteria_google_true(self):
        subject = FreeProxy(google=True)
        actual_0 = subject._FreeProxy__criteria(self.__tr_elements()[0])
        actual_1 = subject._FreeProxy__criteria(self.__tr_elements()[1])
        self.assertEqual(False, actual_0)
        self.assertEqual(True, actual_1)

    def __tr_elements(self):
        return lh.fromstring(
            '<tr>'
            '<td>111.111.111.111</td><td>8080</td><td>CN</td><td class="hm">China</td><td>anonymous</td>'
            '<td class="hm">no</td><td class="hx">yes</td><td class="hm">1 min ago</td>'
            '</tr> <tr>'
            '<td>222.222.222.222</td><td>8080</td><td>NL</td><td class="hm">Netherlands</td><td>elite proxy</td>'
            '<td class="hm">yes</td><td class="hx">yes</td><td class="hm">2 mins ago</td>'
            '</tr>'
        ).xpath('//tr')


if __name__ == '__main__':
    unittest.main()
