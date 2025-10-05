# Free-proxy

![Version 1.1.3](https://img.shields.io/badge/Version-1.1.3-blue.svg)

## Get free working proxies from <https://www.sslproxies.org/>, <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html> and <https://free-proxy-list.net>, or https://proxylist.geonode.com/api/proxy-list and https://proxyscrape.com and use them in your script

The FreeProxy class scrapes proxies from <https://www.sslproxies.org/>, <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html>, <https://free-proxy-list.net> or <https://proxylist.geonode.com/api/proxy-list> and <https://proxyscrape.com> and checks to make sure that it works.
You can filter proxies by country, and specify an acceptable timeout. You can also randomize the list of proxies, rather than going in the order that they are scraped in.

You can use this to send requests through a custom proxy, with Selenium, or with anything else.

Returns proxy as string:

```python
'http://113.160.218.14:8888'
```

### Requirements

- [Python 3](https://www.python.org/downloads/)
- [Requests library](https://github.com/psf/requests)
- [Lxml library](https://github.com/lxml/lxml)

### Installation

```python
pip install free-proxy
```

[![asciicast](https://asciinema.org/a/Xolpn3eD2tyJl8Y8HE9zolgex.svg)](https://asciinema.org/a/Xolpn3eD2tyJl8Y8HE9zolgex)

### Usage examples

First import Free Proxy that way:

```python
from fp.fp import FreeProxy
```

## Options

| Parameter  | Type      | Example      | Default value |
| ---------- | --------- | ------------ | ------------- |
| country_id | list      | ['US', 'BR'] | None          |
| timeout    | float > 0 | 0.1          | 0.5           |
| rand       | bool      | True         | False         |
| anonym     | bool      | True         | False         |
| elite      | bool      | True         | False         |
| google     | bool,None | False        | None          |
| https      | bool      | True         | False         |
| url        | str       | ''           | google.com    |
- **No parameters**
  Get the first working proxy from <https://www.sslproxies.org/>. If no proxies are working, try again pulling from <https://free-proxy-list.net>

```python
proxy = FreeProxy().get()
```

- **`country_id` parameter**
  Get the first working proxy from a specified list of countries (from <https://www.sslproxies.org/>). If no proxies are working **check all countries** pulling from <https://free-proxy-list.net>.

```python
proxy = FreeProxy(country_id=['US', 'BR']).get()
```

- **`country_id` for US and GB**
  You can set the country_id to US or GB to get a proxy from the United States or the United Kingdom respectively. Proxies will be scrapped from <https://www.us-proxy.org/> (`US`) or <https://free-proxy-list.net/uk-proxy.html> (`GB`). If there are no working proxies in the specified list **check all countries**

```python
proxy = FreeProxy(country_id=['US']).get()
proxy = FreeProxy(country_id=['GB']).get()
```

- **`timeout` parameter**
  Timeout is the parameter for checking if a proxy is valid. If the server does not respond in specified time,
  the script will mark the proxy as invalid. Default `timeout=0.5`. You can change it by specifying a timeout eg. `timeout=1`.

```python
proxy = FreeProxy(timeout=1).get()
```

- **`rand` parameter**
  Shuffles the order of the proxy list from <https://www.sslproxies.org/> instead of going from newest to oldest (as listed on the website). Defaults to `rand=False`

```python
proxy = FreeProxy(rand=True).get()
```

- **`anonym` parameter**
  Return only proxies marked as anonymous. Defaults to `anonym=False`

```python
proxy = FreeProxy(anonym=True).get()
```

- **`elite` parameter**
  Return only proxies marked as 'elite proxy'. Defaults to `elite=False`.

```python
proxy = FreeProxy(elite=True).get()
```

Please note: elite proxies are always anonymous. If you set `elite=True`, you will also be eliminating any non-anonymous proxies.

- **`google` parameter**
  If `True` it will only return proxies marked as "google". If `False`, it will not return proxies marked as "google". Defaults to `google=None`, which returns all proxies.

```python
proxy = FreeProxy(google=True).get()
```

- **`https` parameter**
  If `True` it will only return proxies marked as HTTPS. Defaults to `https=False` - i.e. HTTP proxy (for HTTP websites).

  Please note: HTTPS proxies work for both HTTP and HTTPS websites.

```python
proxy = FreeProxy(https=True).get()
```

You can combine parameters:

```python
proxy = FreeProxy(country_id=['US', 'BR'], timeout=0.3, rand=True).get()
```

If there are no working proxies with the provided parameters, the script will raise `FreeProxyException` with the message `There are no working proxies at this time.`.

- **`url` parameter**
  The url parameter allows you to set a custom URL for testing purposes. If left empty, it defaults to 'https://www.google.com'.

Using default URL:

```python
proxy = FreeProxy().get() 
```

Using custom URL, if test on different endpoint is needed:

```python
proxy = FreeProxy(url='http://httpbin.org/get').get() 
```

## CHANGELOG

---
## [1.1.3] - 2024-11-07

- Added `url` paramameter

## [1.1.2] - 2024-09-07

- Updated lxml to version 5.3.0
- Updated pip-chill to version 1.0.3
- Updated requests to version 2.32.3

## [1.1.1] - 2023-02-18

- Fixed https parameter error
- Fixed additional loop issue when no proxy was found

## [1.1.0] - 2022-11-12

- Added new website to get proxies from <https://free-proxy-list.net>
- Added new website to get proxies from <https://free-proxy-list.net/uk-proxy.html>
- Added new website to get proxies from <https://www.us-proxy.org/>
- Change lxml version to 4.9.1

## [1.0.6] - 2022-01-23

- Added `google` parameter
- Added `https` parameter

## [1.0.5] - 2022-01-07

- Added `elite` parameter
- Add exception class and raise exception instead of system exit
- Change lxml version to 4.6.5

## [1.0.4] - 2021-11-13

- Fix proxy list default length

## [1.0.3] - 2021-08-18

- Change XPatch due to SSL proxies page update
- Change lxml version

## [1.0.2] - 2020-09-03

- Added `anonym` parameter

## [1.0.1] - 2020-03-19

- Fix typos in readme
- Fix urrlib3 exception `urllib3.exceptions.ProxySchemeUnknown: Not supported proxy scheme None`,
- Fix imports

## [1.0.0] - 2019-02-04

- Initial release

## Disclaimer

The authors of this repository are not responsible for any consequences, damages or losses arising from the use or misuse of this repository or content. Users are solely responsible for their actions and any consequences that may follow.

## License

---

[MIT](https://github.com/jundymek/free-proxy/blob/master/LICENSE)

**Free Software!**
