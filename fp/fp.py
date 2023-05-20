#!/usr/bin/env python3

import asyncio
import random
import re

import aiohttp
import lxml.html as lh
from fp.errors import FreeProxyException


class FreeProxy:
    """
    FreeProxy class scrapes proxies from <https://www.sslproxies.org/>,
    <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html>,
    and <https://free-proxy-list.net> and checks if proxy is working.
    There is possibility to filter proxies by country and acceptable timeout.
    You can also randomize list of proxies from where script would get first
    working proxy.
    """

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False, elite=False, google=None, https=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'

    async def get_proxy_list(self, repeat):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.__website(repeat)) as response:
                    response.raise_for_status()
                    content = await response.text()
            doc = lh.fromstring(content)
        except aiohttp.ClientError as e:
            raise FreeProxyException(f'Request to {self.__website(repeat)} failed') from e

        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}'
                       for i in range(1, len(tr_elements)) if self.__criteria(tr_elements[i])]
            return proxies
        except Exception as e:
            raise FreeProxyException('Failed to get list of proxies') from e

    def __website(self, repeat):
        if repeat:
            return "https://free-proxy-list.net"
        elif self.country_id == ['US']:
            return 'https://www.us-proxy.org'
        elif self.country_id == ['GB']:
            return 'https://free-proxy-list.net/uk-proxy.html'
        else:
            return 'https://www.sslproxies.org'

    def __criteria(self, row_elements):
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

    async def get(self, repeat=False):
        """Returns a working proxy that matches the specified parameters."""
        proxy_list = await self.get_proxy_list(repeat)
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = None
        async with aiohttp.ClientSession() as session:
            for proxy_address in proxy_list:
                proxies = {self.schema: f'http://{proxy_address}'}
                try:
                    working_proxy = await self.__check_if_proxy_is_working(session, proxies)
                    if working_proxy:
                        return working_proxy
                except aiohttp.ClientError:
                    continue
        if not working_proxy and not repeat:
            if self.country_id is not None:
                self.country_id = None
            return await self.get(repeat=True)
        raise FreeProxyException('There are no working proxies at this time.')

    async def __check_if_proxy_is_working(self, session, proxies):
        url = f'{self.schema}://www.google.com'
        try:
            async with session.get(url, proxy=proxies[self.schema], timeout=self.timeout) as response:
                if response.status == 200:
                    if response.connection:
                        pattern = r"URL\('(.+?)'\)"
                        match = re.search(pattern, str(response.connection))
                        if match:
                            return proxies[self.schema]
                        else:
                            pass
        except asyncio.TimeoutError:
            pass
        except aiohttp.ClientError:
            pass

        return None
