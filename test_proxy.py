import unittest
import requests
from free_proxy import FreeProxy


class TestProxy(unittest.TestCase):

    def test_proxy_without_parameters(self):
        x = FreeProxy().get()
        page = requests.get('http://icanhazip.com', proxies={'http': x})
        self.assertEqual(page.content.decode("utf-8").strip(), x.split(':')[0])

    def test_proxy_with_country_id_parameter(self):
        x = FreeProxy(country_id='US').get()
        page = requests.get('http://icanhazip.com', proxies={'http': x})
        self.assertEqual(page.content.decode("utf-8").strip(), x.split(':')[0])
