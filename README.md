# Free-proxy

## Get free working proxy from <https://www.sslproxies.org/> and use it in your script

FreeProxy class scrapes proxies from <https://www.sslproxies.org/> and checkes if proxy is working. There is posibility to  
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

- **No parameters**  
  Get first working proxy from 100 proxies from <https://www.sslproxies.org/>

```python
proxy = FreeProxy().get()
```

- **`country_id` parameter**  
  Get first working proxy from specified list of countries. If there is no valid proxy from specified list check all countries

```python
proxy = FreeProxy(country_id=['US', 'BR']).get()
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

You can combine parameters:

```python
proxy = FreeProxy(country_id=['US', 'BR'], timeout=0.3, rand=True).get()
```

If there is no working proxy script returns `None`

## CHANGELOG

---
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
