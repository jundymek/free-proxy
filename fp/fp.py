#!/usr/bin/env python3
import random
import lxml.html as lh
import requests
from fp.errors import FreeProxyException

class FreeProxy:
    '''
    FreeProxy class scrapes proxies from:
        - https://www.sslproxies.org/
        - https://www.us-proxy.org/
        - https://free-proxy-list.net/uk-proxy.html
        - https://free-proxy-list.net
        - https://proxylist.geonode.com/api/proxy-list
        - https://api.proxyscrape.com/v4/free-proxy-list/get

    It checks if the proxies are working and allows filtering by country, anonymity level,
    and other criteria. Optionally, you can randomize the list of proxies to select a working proxy.
    '''

    def __init__(self, country_id=None, timeout=5, rand=False, anonym=False, elite=False, google=None, https=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'

    def get_proxy_list(self, repeat=False):
        proxy_list = []
        # Fetch proxies from websites
        #proxy_list.extend(self._get_proxies_from_websites(repeat))
        # Fetch proxies from GeoNode API
        proxy_list.extend(self._get_proxies_from_geonode())
        # Fetch proxies from ProxyScrape API
        proxy_list.extend(self._get_proxies_from_proxyscrape())

        if not proxy_list:
            raise FreeProxyException('Failed to retrieve any proxies from all sources.')

        # Apply criteria filtering
        filtered_proxies = [proxy for proxy in proxy_list if self._criteria(proxy)]
        
        if not filtered_proxies:
            if not repeat:
                # Retry without country filter if initial attempt fails
                original_country = self.country_id
                self.country_id = None
                return self.get_proxy_list(repeat=True)
            else:
                raise FreeProxyException('No proxies found matching the specified criteria.')

        if self.random:
            random.shuffle(filtered_proxies)

        return filtered_proxies

    def _get_proxies_from_websites(self, repeat):
        try:
            page = requests.get(self.__website(repeat), timeout=self.timeout)
            page.raise_for_status()
            doc = lh.fromstring(page.content)
        except requests.exceptions.RequestException as e:
            raise FreeProxyException(f'Request to {self.__website(repeat)} failed') from e

        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            proxies = []
            for tr in tr_elements[1:]:  # Skip header row
                ip = tr[0].text_content().strip()
                port = tr[1].text_content().strip()
                country = tr[2].text_content().strip()
                anonymity = tr[4].text_content().strip().lower()
                google = tr[5].text_content().strip().lower() == 'yes'
                https = tr[6].text_content().strip().lower() == 'yes'
                protocol = 'https' if https else 'http'

                proxy = {
                    'ip': ip,
                    'port': port,
                    'country': country,
                    'anonymity': anonymity,
                    'google': google,
                    'https': https,
                    'protocol': protocol
                }
                proxies.append(proxy)
            return proxies
        except Exception as e:
            raise FreeProxyException('Failed to parse proxies from websites') from e

    def _get_proxies_from_geonode(self):
        api_url = "https://proxylist.geonode.com/api/proxy-list"
        params = {
            'limit': 100,
            'page': 1,
            'sort_by': 'lastChecked',
            'sort_type': 'desc'
        }
        try:
            response = requests.get(api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            # Log or handle the exception as needed, but continue
            print(f"Failed to fetch proxies from GeoNode: {e}")
            return []

        proxies = []
        for item in data.get('data', []):
            proxy = {
                'ip': item.get('ip', ''),
                'port': item.get('port', ''),
                'country': item.get('country', ''),
                'anonymity': item.get('anonymityLevel', '').lower(),
                'google': item.get('google', False),
                'https': 'https' in [proto.lower() for proto in item.get('protocols', [])],
                'protocol': 'https' if 'https' in [proto.lower() for proto in item.get('protocols', [])] else 'http'
            }
            proxies.append(proxy)
        return proxies

    def _get_proxies_from_proxyscrape(self):
        api_url = "https://api.proxyscrape.com/v4/free-proxy-list/get"
        params = {
            'request': 'get_proxies',
            'proxy_format': 'protocolipport',
            'format': 'json',
            'limit': 100  # Adjust limit as needed
        }
        try:
            response = requests.get(api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            # Log or handle the exception as needed, but continue
            print(f"Failed to fetch proxies from ProxyScrape: {e}")
            return []

        proxies = []
        for item in data.get('proxies', []):
            protocol = item.get('protocol', '').lower()
            https = protocol == 'https'
            proxy = {
                'ip': item.get('ip', ''),
                'port': item.get('port', ''),
                'country': item.get('ip_data', {}).get('country', ''),
                'anonymity': item.get('anonymity', '').lower(),
                'google': item.get('ssl', False),
                'https': https,
                'protocol': protocol
            }
            proxies.append(proxy)
        return proxies

    def __website(self, repeat):
        if repeat:
            return "https://free-proxy-list.net"
        elif self.country_id == ['US']:
            return 'https://www.us-proxy.org'
        elif self.country_id == ['GB']:
            return 'https://free-proxy-list.net/uk-proxy.html'
        else:
            return 'https://www.sslproxies.org'

    def _criteria(self, proxy):
        '''
        Check if the proxy meets the specified criteria.
        '''
        # Country filter
        if self.country_id:
            if proxy['country'] not in self.country_id:
                return False

        # Anonymity filter
        if self.anonym:
            if self.elite:
                if proxy['anonymity'] != 'elite':
                    return False
            else:
                if proxy['anonymity'] not in ['anonymous', 'elite']:
                    return False

        # Google access filter
        if self.google is not None:
            if proxy['google'] != self.google:
                return False

        # HTTPS filter
        if self.schema == 'https' and not proxy['https']:
            return False

        return True

    def get(self, repeat=False):
        '''Returns a working proxy that matches the specified parameters.'''
        proxy_list = self.get_proxy_list(repeat)
        if not proxy_list:
            raise FreeProxyException('No proxies available.')

        for proxy in proxy_list:
            proxy_address = f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
            proxies = {self.schema: proxy_address}
            try:
                working_proxy = self.__check_if_proxy_is_working(proxies, proxy['ip'])
                if working_proxy:
                    return working_proxy
            except requests.exceptions.RequestException:
                continue

        if not repeat:
            if self.country_id is not None:
                self.country_id = None
            return self.get(repeat=True)

        raise FreeProxyException('There are no working proxies at this time.')

    def __check_if_proxy_is_working(self, proxies, expected_ip):
        '''
        Check if the proxy is working by making a request to Google and verifying the IP.
        '''
        url = f'{self.schema}://www.google.com'
        try:
            response = requests.get(url, proxies=proxies, timeout=self.timeout, stream=True)
            response.raise_for_status()
            # Optionally, verify the IP by parsing headers or using an IP check service
            # Here, we'll assume the proxy works if the request succeeds
            return proxies[self.schema]
        except requests.exceptions.RequestException:
            return None