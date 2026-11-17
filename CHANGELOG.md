## [1.3.1] - 2026-11-16

- Fixed proxy list parsing after the source sites changed their table layout: proxies came back as `ip:port:HTTP`, which made every check fail and `get()` always raise "There are no working proxies", and the `elite`, `anonym` and `https` filters returned nothing. Columns are now looked up by header name, and a layout without the expected columns raises `FreeProxyException` naming the missing columns instead of silently returning bad addresses (#64)
- Fixed `AsyncFreeProxy.get()` crashing with `AttributeError` on aiohttp 3.8.x when a proxy dropped the connection during the TLS handshake. Any error while checking a single proxy now just marks that proxy as not working
- Proxy lists are downloaded directly from free-proxy-list.net: sslproxies.org and us-proxy.org now only redirect there, which cost an extra request and would break if the old domains stopped redirecting
- SOCKS proxies from the source lists are skipped: they cannot be used through an `http://` proxy URL
- Deprecated the `google` parameter: the source sites no longer publish this information, so it is ignored and emits a `DeprecationWarning`. It will be removed in the next major release

## [1.3.0] - 2026-09-06

- Added `AsyncFreeProxy` — an asyncio variant of `FreeProxy` that checks proxies concurrently and returns the first working one (based on the idea from #39, thanks @NerdzzyDev)
- Async support is an optional extra: `pip install "free-proxy[async]"` (installs aiohttp)
- Added `max_concurrent` parameter to `AsyncFreeProxy` (default: 20) limiting how many proxies are checked at once
- Raised minimum Python version to 3.9

## [1.2.3] - 2026-08-24

- Fixed the proxy check silently bypassing the proxy when the test URL scheme did not match the `https` setting. With default settings (HTTP proxy mapping + HTTPS test URL) `requests` selected no proxy at all, the peername verification then rejected every candidate and `get()` always failed. The proxies mapping now covers both `http` and `https` schemes. Broken since 1.2.1. (#61)
- Added a CI workflow running the test suite on Python 3.9–3.13

## [1.2.2] - 2026-07-04

- Fixed `get_proxy_list` hanging indefinitely when a source website stalls — the proxy list request now has a timeout (#58)
- Added `request_timeout` parameter (default: 10 seconds) to control the proxy list download timeout

## [1.2.1] - 2026-06-09

- Fixed proxy check failing due to a duplicated URL schema (`http://https://...`), introduced in 1.1.3. This broke `https=True` and custom `url` usage (#52, #43).

## [1.2.0] - 2026-06-09

- Updated lxml to version 6.1.1
- Updated requests to version 2.34.2
- Updated pip-chill to version 1.0.5
- Pinned minimum dependency versions in `install_requires` (`lxml>=5.0,<7`, `requests>=2.31,<3`)
- Raised minimum Python version to 3.8

## [1.1.3] - 2024-11-07

- Added `url` paramameter

## [1.1.2] - 2024-07-29

- Updated lxml to version 5.3.0
- Updated pip-chill to version 1.0.3
- Updated requests to version 2.32.3

## [1.1.1] - 2023-02-18

- Fixed https parameter error
- Fixed additional loop issue when no proxy was found

## [1.1.0] - 2022-11-12

- Added new website to get proxies from: <https://free-proxy-list.net>
- Added new website to get proxies from: <https://free-proxy-list.net/uk-proxy.html>
- Added new website to get proxies from: <https://www.us-proxy.org/>
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
