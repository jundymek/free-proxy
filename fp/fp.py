#!/usr/bin/env python3

import asyncio
import random

import lxml.html as lh
import requests

from fp.errors import FreeProxyException

try:
    import aiohttp
except ImportError:
    # Optional dependency -- install with: pip install "free-proxy[async]"
    aiohttp = None


class FreeProxy:
    '''
    FreeProxy class scrapes proxies from <https://www.sslproxies.org/>,
    <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html>,
    and <https://free-proxy-list.net> and checks if proxy is working.
    There is possibility to filter proxies by country and acceptable timeout.
    You can also randomize list of proxies from where script would get first
    working proxy.
    '''

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False, elite=False, google=None, https=False, url='https://www.google.com', request_timeout=10):
        self.country_id = country_id
        self.timeout = timeout
        self.request_timeout = request_timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'
        self.url = url

    def get_proxy_list(self, repeat):
        try:
            page = requests.get(self._website(repeat), timeout=self.request_timeout)
        except requests.exceptions.RequestException as e:
            raise FreeProxyException(
                f'Request to {self._website(repeat)} failed') from e
        return self._parse_proxy_list(page.content)

    def _parse_proxy_list(self, content):
        try:
            doc = lh.fromstring(content)
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            return [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}'
                    for i in range(1, len(tr_elements)) if self._criteria(tr_elements[i])]
        except Exception as e:
            raise FreeProxyException('Failed to get list of proxies') from e

    def _website(self, repeat):
        if repeat:
            return "https://free-proxy-list.net"
        elif self.country_id == ['US']:
            return 'https://www.us-proxy.org'
        elif self.country_id == ['GB']:
            return 'https://free-proxy-list.net/uk-proxy.html'
        else:
            return 'https://www.sslproxies.org'

    def _criteria(self, row_elements):
        country_criteria = True if not self.country_id else row_elements[2].text_content(
        ) in self.country_id
        elite_criteria = True if not self.elite else 'elite' in row_elements[4].text_content(
        )
        anonym_criteria = True if (
            not self.anonym) or self.elite else 'anonymous' == row_elements[4].text_content()
        switch = {'yes': True, 'no': False}
        google_criteria = True if self.google is None else self.google == switch.get(
            row_elements[5].text_content())
        https_criteria = True if self.schema == 'http' else row_elements[6].text_content(
        ).lower() == 'yes'
        return country_criteria and elite_criteria and anonym_criteria and google_criteria and https_criteria

    def get(self, repeat=False):
        '''Returns a working proxy that matches the specified parameters.'''
        proxy_list = self.get_proxy_list(repeat)
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = None
        for proxy_address in proxy_list:
            # requests selects the proxy by the URL scheme, so the mapping
            # must cover both -- otherwise e.g. an https test URL with the
            # default http schema bypasses the proxy entirely.
            proxies = {'http': f'http://{proxy_address}',
                       'https': f'http://{proxy_address}'}
            try:
                working_proxy = self.__check_if_proxy_is_working(proxies)
                if working_proxy:
                    return working_proxy
            except requests.exceptions.RequestException:
                continue
        if not working_proxy and not repeat:
            if self.country_id is not None:
                self.country_id = None
            return self.get(repeat=True)
        raise FreeProxyException(
            'There are no working proxies at this time.')

    def __check_if_proxy_is_working(self, proxies):
        url = self.url
        ip = proxies[self.schema].split(':')[1][2:]
        with requests.get(url, proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw.connection.sock and r.raw.connection.sock.getpeername()[0] == ip:
                return proxies[self.schema]
        return


class AsyncFreeProxy(FreeProxy):
    '''
    Asynchronous variant of FreeProxy built on aiohttp. Requires the "async"
    extra: pip install "free-proxy[async]".

    Public methods mirror FreeProxy but are coroutines: call them with await
    from your own event loop, or via asyncio.run() in a plain script:

        proxy = asyncio.run(AsyncFreeProxy().get())

    Proxies are checked concurrently (up to max_concurrent at a time) and the
    first working one wins; remaining checks are cancelled.
    '''

    def __init__(self, *args, max_concurrent=20, **kwargs):
        if aiohttp is None:
            raise FreeProxyException(
                'aiohttp is not installed. Install async support with: pip install "free-proxy[async]"')
        if not isinstance(max_concurrent, int) or max_concurrent < 1:
            # 0 would park every task on the semaphore forever -- the
            # request timeout never starts while waiting for a slot.
            raise ValueError('max_concurrent must be a positive integer')
        super().__init__(*args, **kwargs)
        self.max_concurrent = max_concurrent

    async def get_proxy_list(self, repeat):
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self._website(repeat)) as response:
                    content = await response.read()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise FreeProxyException(
                f'Request to {self._website(repeat)} failed') from e
        return self._parse_proxy_list(content)

    async def get(self, repeat=False):
        '''Returns a working proxy that matches the specified parameters.'''
        proxy_list = await self.get_proxy_list(repeat)
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = await self._find_working_proxy(proxy_list)
        if working_proxy:
            return working_proxy
        if not repeat:
            if self.country_id is not None:
                self.country_id = None
            return await self.get(repeat=True)
        raise FreeProxyException(
            'There are no working proxies at this time.')

    async def _find_working_proxy(self, proxy_list):
        semaphore = asyncio.Semaphore(self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [asyncio.create_task(self._check_if_proxy_is_working(session, semaphore, proxy_address))
                     for proxy_address in proxy_list]
            try:
                for finished in asyncio.as_completed(tasks):
                    working_proxy = await finished
                    if working_proxy:
                        return working_proxy
                return None
            finally:
                # Cancel unfinished checks (no-op for finished tasks) and let
                # the cancellations settle before the session closes under them.
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_if_proxy_is_working(self, session, semaphore, proxy_address):
        async with semaphore:
            try:
                async with session.get(self.url, proxy=f'http://{proxy_address}') as response:
                    connection = response.connection
                    if connection is None or connection.transport is None:
                        return None
                    peername = connection.transport.get_extra_info('peername')
                    if peername and peername[0] == proxy_address.split(':')[0]:
                        return f'http://{proxy_address}'
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
                pass
            return None
