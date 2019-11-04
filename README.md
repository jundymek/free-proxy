
# Free-proxy  
  
## Get free working proxy from https://www.sslproxies.org/ and use it in your script  
  
FreeProxy class scrapes proxies from https://www.sslproxies.org/ and checkes if proxy is working. There is posibility to  
filter proxies by country and acceptable timeout. You can also randomize list of proxies from where script would get   
first working proxy.  
  
You can use it in sending request through custom proxy, with selenium or wherever you want.  
  
Returns proxy as string:  
```  
'113.160.218.14:8888'  
```  
  
### Requirements  
  
* Python3  
  
* Request library  
  
* Lxml library  
  
### Usage with examples  


Parameter | Type| Example | Default value
--- | --- | --- | --- 
country_id | str | 'US' | None
timeout | float > 0 |0.1 | 0.5
rand | bool | True | False

  
* **No parameters**   
Get first working proxy from 100 proxies from https://www.sslproxies.org/  
```
proxy = FreeProxy().get()  
```  
* **`country_id` parameter**   
Get first working proxy from specified country. If there is no valid proxy from specified country check all countries  
```  
proxy = FreeProxy(country_id='US').get()  
```  
* **`timeout` parameter**   
Timeout is parameter for checking if proxy is valid. If test site doesn't respond in specified time  
script marks this proxy as invalid. Default ```timeout=0.5```. You can change it by defining  
specified timeout eg. ```timeout=1```.  
```  
proxy = FreeProxy(timeut=1).get()  
```  
* **`rand` parameter** 
```
proxy = FreeProxy(rand=True).get()  
```  
  
Shuffles proxy list from https://www.sslproxies.org/. Default `rand=False` and searches for working proxy from newest 
to oldest (as they are listed in https://www.sslproxies.org/).
  
You can combine parameters:  
```  
proxy = FreeProxy(country_id='US', timeout=0.3, rand=True).get()  
```  
  
If there is no working proxy script returns `None`  

  
  
License  
----  
  
MIT  
  
  
**Free Software!**