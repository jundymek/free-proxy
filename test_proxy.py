import asyncio
import os
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import lxml.html as lh
import requests

import aiohttp

from fp.errors import FreeProxyException
from fp.fp import AsyncFreeProxy, FreeProxy

SKIP_NETWORK = os.getenv('CI') == 'true'


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

    @unittest.skipIf(SKIP_NETWORK, 'hits real proxy-list sites')
    def test_anonym_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list(repeat=False))
        test2 = FreeProxy(anonym=True)
        cnt2 = len(test2.get_proxy_list(repeat=False))
        self.assertTrue(cnt2 < cnt1)

    @unittest.skipIf(SKIP_NETWORK, 'hits real proxy-list sites')
    def test_elite_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list(repeat=False))
        test2 = FreeProxy(elite=True)
        cnt2 = len(test2.get_proxy_list(repeat=False))
        self.assertTrue(cnt2 < cnt1)

    @unittest.skipIf(SKIP_NETWORK, 'hits real proxy-list sites')
    def test_google_filter(self):
        test1 = FreeProxy()
        cnt1 = len(test1.get_proxy_list(repeat=False))
        test2 = FreeProxy(google=True)
        test3 = FreeProxy(google=False)
        cnt2 = len(test2.get_proxy_list(repeat=False))
        cnt3 = len(test3.get_proxy_list(repeat=False))
        self.assertTrue(cnt2 < cnt1)
        self.assertTrue(cnt3 < cnt1)

    def test_criteria_defaults(self):
        '''Default settings: anonym = False, elite = False, google = None'''
        subject = FreeProxy()
        actual_0 = subject._criteria(self.__tr_elements()[0])
        actual_1 = subject._criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(True, actual_1)

    def test_criteria_anonym_true(self):
        subject = FreeProxy(anonym=True)
        actual_0 = subject._criteria(self.__tr_elements()[0])
        actual_1 = subject._criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(False, actual_1)

    def test_criteria_elite_true(self):
        subject = FreeProxy(elite=True)
        actual_0 = subject._criteria(self.__tr_elements()[0])
        actual_1 = subject._criteria(self.__tr_elements()[1])
        self.assertEqual(False, actual_0)
        self.assertEqual(True, actual_1)

    def test_criteria_google_false(self):
        subject = FreeProxy(google=False)
        actual_0 = subject._criteria(self.__tr_elements()[0])
        actual_1 = subject._criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(False, actual_1)

    def test_criteria_google_true(self):
        subject = FreeProxy(google=True)
        actual_0 = subject._criteria(self.__tr_elements()[0])
        actual_1 = subject._criteria(self.__tr_elements()[1])
        self.assertEqual(False, actual_0)
        self.assertEqual(True, actual_1)

    def test_criteria_https_true(self):
        subject = FreeProxy(https=True)
        actual_0 = subject._criteria(self.__tr_elements()[0])
        actual_1 = subject._criteria(self.__tr_elements()[1])
        self.assertEqual(True, actual_0)
        self.assertEqual(False, actual_1)

    def test_country_id_us_page_first_loop(self):
        subject = FreeProxy(country_id=['US'])
        actual = subject._website(repeat=False)
        self.assertEqual('https://www.us-proxy.org', actual)

    def test_country_id_us_page_second_loop(self):
        subject = FreeProxy(country_id=['US'])
        actual = subject._website(repeat=True)
        self.assertEqual('https://free-proxy-list.net', actual)

    def test_country_id_gb_page_first_loop(self):
        subject = FreeProxy(country_id=['GB'])
        actual = subject._website(repeat=False)
        self.assertEqual('https://free-proxy-list.net/uk-proxy.html', actual)

    def test_country_id_gb_page_second_loop(self):
        subject = FreeProxy(country_id=['GB'])
        actual = subject._website(repeat=True)
        self.assertEqual('https://free-proxy-list.net', actual)

    def default_page_first_loop(self):
        subject = FreeProxy()
        actual = subject._website(repeat=False)
        self.assertEqual('https://www.sslproxies.org', actual)

    def default_page_second_loop(self):
        subject = FreeProxy()
        actual = subject._website(repeat=True)
        self.assertEqual('https://free-proxy-list.net', actual)

    def test_default_url(self):
        proxy =FreeProxy()
        self.assertEqual(proxy.url, 'https://www.google.com')

    def test_custom_url(self):
        proxy = FreeProxy(url='http://httpbin.org/get')
        self.assertEqual(proxy.url, 'http://httpbin.org/get')

    @patch('fp.fp.requests.get')
    def test_check_uses_default_url_without_double_schema(self, mock_get):
        '''The default url should be requested as-is, not prefixed with schema again.'''
        mock_get.return_value.__enter__ = lambda s: s
        mock_get.return_value.__exit__ = MagicMock(return_value=False)
        mock_get.return_value.raw.connection.sock = None
        proxy = FreeProxy()
        proxy.get_proxy_list = MagicMock(return_value=['1.2.3.4:8080'])
        try:
            proxy.get()
        except FreeProxyException:
            pass
        requested_url = mock_get.call_args[0][0]
        self.assertEqual('https://www.google.com', requested_url)

    @patch('fp.fp.requests.get')
    def test_check_uses_custom_url_without_double_schema(self, mock_get):
        '''A custom url should be requested as-is, not prefixed with schema again.'''
        mock_get.return_value.__enter__ = lambda s: s
        mock_get.return_value.__exit__ = MagicMock(return_value=False)
        mock_get.return_value.raw.connection.sock = None
        proxy = FreeProxy(url='http://httpbin.org/get')
        proxy.get_proxy_list = MagicMock(return_value=['1.2.3.4:8080'])
        try:
            proxy.get()
        except FreeProxyException:
            pass
        requested_url = mock_get.call_args[0][0]
        self.assertEqual('http://httpbin.org/get', requested_url)

    @patch('fp.fp.requests.get')
    def test_check_sends_proxy_for_both_url_schemes(self, mock_get):
        '''requests picks the proxy by URL scheme; the mapping must cover both,
        otherwise the default https test URL bypasses an http-keyed proxy.'''
        mock_get.return_value.__enter__ = lambda s: s
        mock_get.return_value.__exit__ = MagicMock(return_value=False)
        mock_get.return_value.raw.connection.sock = None
        proxy = FreeProxy()
        proxy.get_proxy_list = MagicMock(return_value=['1.2.3.4:8080'])
        try:
            proxy.get()
        except FreeProxyException:
            pass
        proxies = mock_get.call_args.kwargs.get('proxies')
        self.assertEqual({'http': 'http://1.2.3.4:8080',
                          'https': 'http://1.2.3.4:8080'}, proxies)

    @patch('fp.fp.requests.get')
    def test_check_returns_proxy_when_peername_matches(self, mock_get):
        '''Success path: a proxy whose IP answers the check is returned.'''
        mock_get.return_value.__enter__ = lambda s: s
        mock_get.return_value.__exit__ = MagicMock(return_value=False)
        mock_get.return_value.raw.connection.sock.getpeername.return_value = (
            '1.2.3.4', 8080)
        proxy = FreeProxy()
        proxy.get_proxy_list = MagicMock(return_value=['1.2.3.4:8080'])
        self.assertEqual('http://1.2.3.4:8080', proxy.get())

    def test_default_request_timeout(self):
        proxy = FreeProxy()
        self.assertEqual(proxy.request_timeout, 10)

    def test_custom_request_timeout(self):
        proxy = FreeProxy(request_timeout=2)
        self.assertEqual(proxy.request_timeout, 2)

    @patch('fp.fp.requests.get')
    def test_get_proxy_list_uses_default_request_timeout(self, mock_get):
        '''The proxy list scrape should never run without a timeout (#58).'''
        mock_get.return_value.content = b'<table id="list"></table>'
        proxy = FreeProxy()
        proxy.get_proxy_list(repeat=False)
        self.assertEqual(10, mock_get.call_args.kwargs.get('timeout'))

    @patch('fp.fp.requests.get')
    def test_get_proxy_list_uses_custom_request_timeout(self, mock_get):
        mock_get.return_value.content = b'<table id="list"></table>'
        proxy = FreeProxy(request_timeout=2)
        proxy.get_proxy_list(repeat=False)
        self.assertEqual(2, mock_get.call_args.kwargs.get('timeout'))

    @patch('fp.fp.requests.get')
    def test_get_proxy_list_timeout_raises_free_proxy_exception(self, mock_get):
        '''A stalled source site should surface as FreeProxyException, not hang.'''
        mock_get.side_effect = requests.exceptions.Timeout()
        proxy = FreeProxy()
        self.assertRaisesRegex(
            FreeProxyException, 'Request to .* failed',
            proxy.get_proxy_list, False)

    def __tr_elements(self):
        return lh.fromstring(
            '<tr>'
            '<td>111.111.111.111</td><td>8080</td><td>CN</td><td class="hm">China</td><td>anonymous</td>'
            '<td class="hm">no</td><td class="hx">yes</td><td class="hm">1 min ago</td>'
            '</tr> <tr>'
            '<td>222.222.222.222</td><td>8080</td><td>NL</td><td class="hm">Netherlands</td><td>elite proxy</td>'
            '<td class="hm">yes</td><td class="hx">no</td><td class="hm">2 mins ago</td>'
            '</tr>'
        ).xpath('//tr')


class TestAsyncProxy(unittest.IsolatedAsyncioTestCase):

    async def test_empty_proxy_list(self):
        test = AsyncFreeProxy()
        test.get_proxy_list = AsyncMock(return_value=[])
        with self.assertRaisesRegex(FreeProxyException,
                                    'There are no working proxies at this time.'):
            await test.get()

    async def test_invalid_proxy(self):
        test = AsyncFreeProxy()
        test.get_proxy_list = AsyncMock(return_value=['111.111.11:2222'])
        with self.assertRaisesRegex(FreeProxyException,
                                    'There are no working proxies at this time.'):
            await test.get()

    async def test_first_working_proxy_wins_and_losers_are_cancelled(self):
        test = AsyncFreeProxy()
        test.get_proxy_list = AsyncMock(
            return_value=['1.1.1.1:80', '2.2.2.2:80', '3.3.3.3:80'])

        async def fake_check(session, semaphore, proxy_address):
            if proxy_address == '2.2.2.2:80':
                await asyncio.sleep(0.05)
                return 'http://2.2.2.2:80'
            await asyncio.sleep(10)
            return None

        test._check_if_proxy_is_working = fake_check
        start = time.perf_counter()
        result = await test.get()
        elapsed = time.perf_counter() - start
        self.assertEqual('http://2.2.2.2:80', result)
        # Slow losers sleep 10s; an early return without cancellation
        # (or a gather-style wait-for-all) would blow way past this.
        self.assertLess(elapsed, 5)

    async def test_semaphore_limits_concurrency(self):
        test = AsyncFreeProxy(max_concurrent=2)
        test.get_proxy_list = AsyncMock(
            return_value=[f'1.1.1.{i}:80' for i in range(6)])
        running = 0
        max_running = 0

        async def fake_check(session, semaphore, proxy_address):
            nonlocal running, max_running
            async with semaphore:
                running += 1
                max_running = max(max_running, running)
                await asyncio.sleep(0.01)
                running -= 1
                return None

        test._check_if_proxy_is_working = fake_check
        with self.assertRaises(FreeProxyException):
            await test.get()
        self.assertEqual(2, max_running)

    def test_invalid_max_concurrent_raises(self):
        for value in (0, -5):
            with self.assertRaisesRegex(ValueError, 'positive integer'):
                AsyncFreeProxy(max_concurrent=value)

    def _mock_session(self, response):
        session = MagicMock()
        session.get.return_value.__aenter__ = AsyncMock(return_value=response)
        session.get.return_value.__aexit__ = AsyncMock(return_value=False)
        return session

    async def test_check_returns_proxy_when_peername_matches(self):
        response = MagicMock()
        response.connection.transport.get_extra_info.return_value = ('1.2.3.4', 8080)
        test = AsyncFreeProxy()
        result = await test._check_if_proxy_is_working(
            self._mock_session(response), asyncio.Semaphore(1), '1.2.3.4:8080')
        self.assertEqual('http://1.2.3.4:8080', result)

    async def test_check_rejects_proxy_when_peername_differs(self):
        response = MagicMock()
        response.connection.transport.get_extra_info.return_value = ('9.9.9.9', 443)
        test = AsyncFreeProxy()
        result = await test._check_if_proxy_is_working(
            self._mock_session(response), asyncio.Semaphore(1), '1.2.3.4:8080')
        self.assertIsNone(result)

    async def test_check_treats_client_error_as_failed_candidate(self):
        session = MagicMock()
        session.get.side_effect = aiohttp.ClientError()
        test = AsyncFreeProxy()
        result = await test._check_if_proxy_is_working(
            session, asyncio.Semaphore(1), '1.2.3.4:8080')
        self.assertIsNone(result)

    async def test_fallback_round_clears_country_and_repeats(self):
        test = AsyncFreeProxy(country_id=['US'])
        test.get_proxy_list = AsyncMock(side_effect=[[], ['1.2.3.4:8080']])
        test._find_working_proxy = AsyncMock(
            side_effect=[None, 'http://1.2.3.4:8080'])
        result = await test.get()
        self.assertEqual('http://1.2.3.4:8080', result)
        self.assertIsNone(test.country_id)
        test.get_proxy_list.assert_awaited_with(True)

    def test_missing_aiohttp_raises_with_install_hint(self):
        with patch('fp.fp.aiohttp', None):
            with self.assertRaisesRegex(FreeProxyException, r'free-proxy\[async\]'):
                AsyncFreeProxy()

    def test_constructor_params_match_sync(self):
        proxy = AsyncFreeProxy(country_id=['US'], timeout=1.5,
                               url='http://httpbin.org/get', max_concurrent=5)
        self.assertEqual(['US'], proxy.country_id)
        self.assertEqual(1.5, proxy.timeout)
        self.assertEqual('http://httpbin.org/get', proxy.url)
        self.assertEqual(5, proxy.max_concurrent)


if __name__ == '__main__':
    unittest.main()
