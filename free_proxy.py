import sys
import requests
import random
import lxml.html as lh


class FreeProxy:

    def __init__(self, country_id=None, timeout=0.5, rand=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
            tr_elements = doc.xpath('//*[@id="proxylisttable"]//tr')
            if not self.country_id:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in range(1, 101)]
            else:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in range(1, 101)
                           if tr_elements[i][2].text_content() == self.country_id]
            return proxies
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get(self):
        proxy_list = self.get_proxy_list()
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
                    response = requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout)
                    print(i, response)
                    if response.status_code == 200:
                        working_proxy = proxy_list[i]
                        break
                except requests.exceptions.RequestException:
                    print(f'{i}: failed')
                    continue
            break
        if working_proxy:
            print(working_proxy)
        else:
            if self.country_id is not None:
                self.country_id = None
                return self.get()
            else:
                print('There are no working proxies at this time.')
                sys.exit(1)
        return working_proxy


if __name__ == '__main__':
    main = FreeProxy(country_id='PL').get()
