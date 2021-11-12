#!/usr/bin/env python3

import random
import sys

import lxml.html as lh
import requests


class FreeProxy:

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False):
        self.country_id = [] if country_id is None else country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            if not self.country_id:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                           range(1, 101)
                           if((tr_elements[i][4].text_content()) == 'anonymous' if self.anonym else True)]  # check the 5th column for `anonymous` if needed
            else:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                           range(1, 101)
                           if tr_elements[i][2].text_content() in self.country_id
                           and ((tr_elements[i][4].text_content()) == 'anonymous' if self.anonym else True)]  # check the 5th column for `anonymous` if needed
            return proxies
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get(self, any_country_on_failure=True):
        proxy_list = self.get_proxy_list()
        if self.random:
            random.shuffle(proxy_list)
            proxy_list = proxy_list
        working_proxy = None
        for i in range(len(proxy_list)):
            proxies = {
                'http': "http://" + proxy_list[i],
            }
            try:
                if self.check_if_proxy_is_working(proxies):
                    working_proxy = self.check_if_proxy_is_working(proxies)
                    return working_proxy
            except requests.exceptions.RequestException:
                continue
        if not working_proxy:
            if any_country_on_failure and self.country_id is not None:
                self.country_id = None
                return self.get()
            else:
                raise RuntimeError('There are no working proxies at this time.')

    def check_if_proxy_is_working(self, proxies):
        with requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw.connection.sock:
                if r.raw.connection.sock.getpeername()[0] == proxies['http'].split(':')[1][2:]:
                    return proxies['http']
