import asyncio
import inspect
import os
import time
import unittest
import warnings
from unittest.mock import AsyncMock, MagicMock, patch

import requests

import aiohttp

from fp.errors import FreeProxyException
from fp.fp import AsyncFreeProxy, FreeProxy

SKIP_NETWORK = os.getenv('CI') == 'true'


def proxy_table(header, rows):
    '''Builds a proxy list page shaped like free-proxy-list.net.'''
    head = ''.join(f'<th>{name}</th>' for name in header)
    body = ''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
                   for row in rows)
    return (f'<html><body><section id="list"><table>'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody>'
            f'</table></section></body></html>').encode()


# Layout used by all source sites since November 2026 (issue #64).
PROXY_LIST_PAGE = proxy_table(
    ['IP:Port', 'Protocol', 'Code', 'Country', 'Anonymity', 'Https', 'Last Checked'],
    [
        ['111.111.111.111:8080', 'HTTP', 'CN', 'China', 'Anonymous', 'Yes', '1 min ago'],
        ['122.122.122.122:3128', 'HTTP', 'NL', 'Netherlands', 'Elite', 'No', '2 mins ago'],
        ['133.133.133.133:1080', 'SOCKS4', 'US', 'United States', 'Elite', 'Yes', '3 mins ago'],
        ['144.144.144.144:80', 'HTTP', 'US', 'United States', 'Transparent', 'No', '4 mins ago'],
    ])

# Layout used before November 2026: separate IP and port columns.
OLD_PROXY_LIST_PAGE = proxy_table(
    ['IP Address', 'Port', 'Code', 'Country', 'Anonymity', 'Google', 'Https', 'Last Checked'],
    [['111.111.111.111', '8080', 'CN', 'China', 'anonymous', 'no', 'yes', '1 min ago']])


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

    def test_country_id_us_page_first_loop(self):
        subject = FreeProxy(country_id=['US'])
        actual = subject._website(repeat=False)
        self.assertEqual('https://free-proxy-list.net/us-proxy.html', actual)

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

    def test_default_page_first_loop(self):
        subject = FreeProxy()
        actual = subject._website(repeat=False)
        self.assertEqual('https://free-proxy-list.net/ssl-proxy.html', actual)

    def test_default_page_second_loop(self):
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
        mock_get.return_value.content = PROXY_LIST_PAGE
        proxy = FreeProxy()
        proxy.get_proxy_list(repeat=False)
        self.assertEqual(10, mock_get.call_args.kwargs.get('timeout'))

    @patch('fp.fp.requests.get')
    def test_get_proxy_list_uses_custom_request_timeout(self, mock_get):
        mock_get.return_value.content = PROXY_LIST_PAGE
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


class TestParseProxyList(unittest.TestCase):

    def parse(self, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            subject = FreeProxy(**kwargs)
        return subject._parse_proxy_list(PROXY_LIST_PAGE)

    def test_defaults_return_ip_port_of_http_proxies(self):
        self.assertEqual(
            ['111.111.111.111:8080', '122.122.122.122:3128', '144.144.144.144:80'],
            self.parse())

    def test_socks_proxies_are_skipped(self):
        '''SOCKS proxies cannot be used through an http:// proxy URL.'''
        socks = [p for p in self.parse() if p.startswith('133.133.133.133')]
        self.assertEqual([], socks)

    def test_anonym_returns_only_anonymous(self):
        self.assertEqual(['111.111.111.111:8080'], self.parse(anonym=True))

    def test_elite_returns_only_elite(self):
        self.assertEqual(['122.122.122.122:3128'], self.parse(elite=True))

    def test_elite_overrides_anonym(self):
        self.assertEqual(['122.122.122.122:3128'], self.parse(anonym=True, elite=True))

    def test_https_returns_only_https_capable(self):
        self.assertEqual(['111.111.111.111:8080'], self.parse(https=True))

    def test_country_id_filters_by_code(self):
        self.assertEqual(['144.144.144.144:80'], self.parse(country_id=['US']))

    def test_google_is_ignored(self):
        '''The source sites no longer publish the Google column.'''
        self.assertEqual(self.parse(), self.parse(google=True))
        self.assertEqual(self.parse(), self.parse(google=False))

    def test_reordered_columns_are_matched_by_name(self):
        page = proxy_table(
            ['Https', 'Anonymity', 'Code', 'Protocol', 'IP:Port'],
            [['Yes', 'Elite', 'DE', 'HTTP', '155.155.155.155:8080']])
        self.assertEqual(['155.155.155.155:8080'],
                         FreeProxy(elite=True, https=True)._parse_proxy_list(page))

    def test_page_without_proxy_table_returns_empty_list(self):
        '''No table (e.g. a maintenance page) is not a layout change: an empty
        list lets get() fall back to the other source.'''
        self.assertEqual([], FreeProxy()._parse_proxy_list(b'<html><body>Maintenance</body></html>'))

    def test_get_falls_back_when_first_page_has_no_table(self):
        pages = {'https://free-proxy-list.net/ssl-proxy.html': b'<html><body>Maintenance</body></html>',
                 'https://free-proxy-list.net': PROXY_LIST_PAGE}
        test = FreeProxy()
        with patch('fp.fp.requests.get') as mock_get:
            mock_get.side_effect = lambda url, **kwargs: MagicMock(content=pages[url])
            proxies = [test.get_proxy_list(repeat) for repeat in (False, True)]
        self.assertEqual([], proxies[0])
        self.assertEqual(3, len(proxies[1]))

    def test_unknown_layout_raises_with_missing_columns(self):
        '''A layout change must fail loudly, not return malformed addresses.'''
        with self.assertRaisesRegex(FreeProxyException, 'missing columns: .*ip:port'):
            FreeProxy()._parse_proxy_list(OLD_PROXY_LIST_PAGE)

    @unittest.skipIf(SKIP_NETWORK, 'hits real proxy-list sites')
    def test_live_list_has_ip_port_format(self):
        proxies = FreeProxy().get_proxy_list(repeat=False)
        self.assertTrue(proxies)
        for proxy in proxies:
            self.assertRegex(proxy, r'^\d{1,3}(\.\d{1,3}){3}:\d+$')


class TestGoogleDeprecation(unittest.TestCase):

    def assert_warns_at_caller(self, cls, **kwargs):
        with self.assertWarnsRegex(DeprecationWarning, 'google') as cm:
            caller_line = inspect.currentframe().f_lineno + 1
            cls(**kwargs)
        # Pointing at the caller makes Python show it by default (PEP 565).
        self.assertEqual((__file__, caller_line), (cm.filename, cm.lineno))

    def test_google_true_warns(self):
        self.assert_warns_at_caller(FreeProxy, google=True)

    def test_google_false_warns(self):
        self.assert_warns_at_caller(FreeProxy, google=False)

    def test_async_google_warns_at_caller(self):
        self.assert_warns_at_caller(AsyncFreeProxy, google=True)

    def test_google_none_does_not_warn(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            FreeProxy()
            AsyncFreeProxy()
        self.assertEqual([], caught)

    def test_google_value_is_kept(self):
        '''Existing code reading the attribute keeps working.'''
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertTrue(FreeProxy(google=True).google)


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

    async def test_check_treats_unexpected_error_as_failed_candidate(self):
        '''aiohttp 3.8.x raises AttributeError when a proxy drops the
        connection during the TLS handshake; one bad proxy must not abort
        the whole search.'''
        session = MagicMock()
        session.get.side_effect = AttributeError(
            "'NoneType' object has no attribute 'get_extra_info'")
        test = AsyncFreeProxy()
        result = await test._check_if_proxy_is_working(
            session, asyncio.Semaphore(1), '1.2.3.4:8080')
        self.assertIsNone(result)

    async def test_check_does_not_swallow_cancellation(self):
        '''Losing checks are cancelled once a winner is found.'''
        session = MagicMock()
        session.get.side_effect = asyncio.CancelledError()
        test = AsyncFreeProxy()
        with self.assertRaises(asyncio.CancelledError):
            await test._check_if_proxy_is_working(
                session, asyncio.Semaphore(1), '1.2.3.4:8080')

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
