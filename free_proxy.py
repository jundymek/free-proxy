import requests
import lxml.html as lh


class FreeProxy:

    def __init__(self, country_id=None, timeout=0.5):
        self.country_id = country_id
        self.timeout = timeout

    def get_proxy_list(self):
        page = requests.get('https://www.sslproxies.org')
        doc = lh.fromstring(page.content)
        tr_elements = doc.xpath('//*[@id="proxylisttable"]//tr')
        proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in range(1, 101)]
        return proxies

    def get_first_working_proxy(self):
        proxy_list = self.get_proxy_list()
        working_proxy = None
        running = True
        while running:
            for i in range(len(proxy_list)):
                proxies = {
                    'http': proxy_list[i],
                    'https': proxy_list[i]
                }
                try:
                    response = requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout)
                    print(i, response)
                    if response.status_code == 200:
                        working_proxy = proxy_list[i]
                        break
                except:
                    print(f'{i}: failed')
                    continue
            break
        print(working_proxy)


if __name__ == '__main__':
    main = FreeProxy()
    main.get_first_working_proxy()
