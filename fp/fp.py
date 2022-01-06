#!/usr/bin/env python3

import random

import lxml.html as lh
import requests

from fp.errors import FreeProxyException


class FreeProxy:
    '''
    FreeProxy class scrapes proxies from <https://www.sslproxies.org/>
    and checks if proxy is working. There is possibility to filter proxies
    by country and acceptable timeout. You can also randomize list
    of proxies from where script would get first working proxy.
    '''

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False, elite=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
        except requests.exceptions.RequestException as e:
            raise FreeProxyException('Request to www.sslproxies.org failed') from e
        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            return [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                        range(1, len(tr_elements)) if self.__criteria(tr_elements[i])]
        except Exception as e:
            raise FreeProxyException('Failed to get list of proxies') from e

    def __criteria(self, row_elements):
        country_criteria = True if not self.country_id else row_elements[2].text_content() in self.country_id
        elite_criteria = True if not self.elite else 'elite' in row_elements[4].text_content()
        anonym_criteria = True if (not self.anonym) or self.elite else 'anonymous' == row_elements[4].text_content()
        return country_criteria and elite_criteria and anonym_criteria

    def get(self):
        '''Returns a proxy that matches the specified parameters.'''
        proxy_list = self.get_proxy_list()
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = None
        while True:
            for proxy_address in proxy_list:
                proxies = {
                    'http': "http://" + proxy_address,
                }
                try:
                    if self.__check_if_proxy_is_working(proxies):
                        working_proxy = self.__check_if_proxy_is_working(
                            proxies)
                        return working_proxy
                except requests.exceptions.RequestException:
                    continue
            break
        if not working_proxy:
            if self.country_id is not None:
                self.country_id = None
                return self.get()
            raise FreeProxyException(
                'There are no working proxies at this time.')

    def __check_if_proxy_is_working(self, proxies):
        with requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw.connection.sock:
                if r.raw.connection.sock.getpeername()[0] == proxies['http'].split(':')[1][2:]:
                    return proxies['http']
        return None
