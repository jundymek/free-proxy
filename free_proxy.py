import random
import sys

import lxml.html as lh
import requests


class FreeProxy:

    def __init__(self, country_id=[], timeout=0.5, rand=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        print(self.country_id)

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
            tr_elements = doc.xpath('//*[@id="proxylisttable"]//tr')
            if not self.country_id:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                           range(1, 101)]
            else:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                           range(1, 101)
                           if tr_elements[i][2].text_content() in self.country_id]
            return proxies
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get(self):
        proxy_list = self.get_proxy_list()
        print(proxy_list)
        if self.random:
            random.shuffle(proxy_list)
            proxy_list = proxy_list
        working_proxy = None
        while True:
            for i in range(len(proxy_list)):
                proxies = {
                    'http': proxy_list[i],
                }
                try:
                    if self.check_if_proxy_is_working(proxies):
                        working_proxy = self.check_if_proxy_is_working(proxies)
                        break
                except requests.exceptions.RequestException:
                    continue
            break
        if not working_proxy:
            if self.country_id is not None:
                self.country_id = None
                return self.get()
            else:
                print('There are no working proxies at this time.')
                return None
        return working_proxy

    def check_if_proxy_is_working(self, proxies):
        with requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw._connection.sock.getpeername()[0] == proxies['http'].split(':')[0]:
                return proxies['http']


if __name__ == '__main__':
    main = FreeProxy(timeout=0.5).get()
