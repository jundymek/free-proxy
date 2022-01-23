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

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False, elite=False, google=None, https=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
        except requests.exceptions.RequestException as e:
            raise FreeProxyException('Request to www.sslproxies.org failed') from e
        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            return [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}'
                    for i in range(1, len(tr_elements)) if self.__criteria(tr_elements[i])]
        except Exception as e:
            raise FreeProxyException('Failed to get list of proxies') from e

    def __criteria(self, row_elements):
        country_criteria = True if not self.country_id else row_elements[2].text_content() in self.country_id
        elite_criteria = True if not self.elite else 'elite' in row_elements[4].text_content()
        anonym_criteria = True if (not self.anonym) or self.elite else 'anonymous' == row_elements[4].text_content()
        switch = {'yes': True, 'no': False}
        google_criteria = True if self.google is None else self.google == switch.get(row_elements[5].text_content())
        return country_criteria and elite_criteria and anonym_criteria and google_criteria

    def get(self):
        '''Returns a proxy that matches the specified parameters.'''
        proxy_list = self.get_proxy_list()
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = None
        for proxy_address in proxy_list:
            proxies = {self.schema: f'{self.schema}://{proxy_address}'}
            try:
                working_proxy = self.__check_if_proxy_is_working(proxies)
                if working_proxy:
                    return working_proxy
            except requests.exceptions.RequestException:
                continue
        if not working_proxy:
            if self.country_id is not None:
                self.country_id = None
                return self.get()
            raise FreeProxyException('There are no working proxies at this time.')

    def __check_if_proxy_is_working(self, proxies):
        url = f'{self.schema}://www.google.com'
        ip = proxies[self.schema].split(':')[1][2:]
        with requests.get(url, proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw.connection.sock and r.raw.connection.sock.getpeername()[0] == ip:
                return proxies[self.schema]
        return
