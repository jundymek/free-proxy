# Free-proxy

## Get free working proxy from <https://www.sslproxies.org/>, <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html> and <https://free-proxy-list.net> and use it in your script

FreeProxy class scrapes proxies from <https://www.sslproxies.org/>, <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html> and <https://free-proxy-list.net> and checks if proxy is working. There is possibility to
filter proxies by country and acceptable timeout. You can also randomize list of proxies from where script would get
first working proxy.

You can use it in sending request through custom proxy, with selenium or wherever you want.

Returns proxy as string:

```python
'http://113.160.218.14:8888'
```

### Requirements

- Python3
- Request library
- Lxml library

### Installation

```python
pip install free-proxy
```

[![asciicast](https://asciinema.org/a/Xolpn3eD2tyJl8Y8HE9zolgex.svg)](https://asciinema.org/a/Xolpn3eD2tyJl8Y8HE9zolgex)

### Usage with examples

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

- **No parameters**
  Get first working proxy from <https://www.sslproxies.org/>. When no proxy is working, repeat once again from <https://free-proxy-list.net>

```python
proxy = FreeProxy().get()
```

- **`country_id` parameter**
  Get first working proxy from specified list of countries (from <https://www.sslproxies.org/>). If there is no valid proxy from specified list **check all countries** from <https://free-proxy-list.net>.

```python
proxy = FreeProxy(country_id=['US', 'BR']).get()
```

- **`country_id` for US and GB**
  You can set country_id to US and GB to get proxy from United States or United Kingdom. In that case proxies will be scrapped from <https://www.us-proxy.org/> (`US`) or <https://free-proxy-list.net/uk-proxy.html> (`GB`) page. If there is no valid proxy from specified list **check all countries**

```python
proxy = FreeProxy(country_id=['US']).get()
proxy = FreeProxy(country_id=['GB']).get()
```

- **`timeout` parameter**
  Timeout is parameter for checking if proxy is valid. If test site doesn't respond in specified time
  script marks this proxy as invalid. Default `timeout=0.5`. You can change it by defining
  specified timeout eg. `timeout=1`.

```python
proxy = FreeProxy(timeout=1).get()
```

- **`rand` parameter**
  Shuffles proxy list from <https://www.sslproxies.org/>. Default `rand=False` and searches for working proxy from newest
  to oldest (as they are listed in <https://www.sslproxies.org/>).

```python
proxy = FreeProxy(rand=True).get()
```

- **`anonym` parameter**
  Return only those proxies that are marked as anonymous. Defaults to `anonym=False`

```python
proxy = FreeProxy(anonym=True).get()
```

- **`elite` parameter**
  Return only those proxies that are marked as 'elite proxy'. Defaults to `elite=False`.

```python
proxy = FreeProxy(elite=True).get()
```

Note that elite proxies are anonymous at the same time, thus `anonym=True` automatically when `elite=True`.

- **`google` parameter**
  If `True` it returns only those proxies that are marked as google, if `False` - as no google. Defaults to `google=None` that returns all proxies.

```python
proxy = FreeProxy(google=True).get()
```

- **`https` parameter**
  If true it returns only those proxies that are marked as HTTPS. Defaults to `https=False` - i.e. HTTP proxy (for HTTP websites).

  Note that HTTPS proxy is for both HTTP and HTTPS websites.

```python
proxy = FreeProxy(https=True).get()
```

You can combine parameters:

```python
proxy = FreeProxy(country_id=['US', 'BR'], timeout=0.3, rand=True).get()
```

If there are no working proxies with provided parameters script raises `FreeProxyException` with `There are no working proxies at this time.` message.

## CHANGELOG

---

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

## License

---

MIT

**Free Software!**
