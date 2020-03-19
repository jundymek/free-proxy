from free_proxy import FreeProxy

x = FreeProxy(country_id=['PL']).get()
# print(x)
# print(type(x))
if x is None:
    print('TAK')
else:
    print('NIE')
# page = requests.get('http://icanhazip.com', proxies={'http': x}, stream=True)
# print(page.raw._connection.sock.getpeername()[0])
# print(x.split(':')[0])
# print(page.raw._connection.sock.getpeername()[0] == str(x.split(':')[0]))

# print(FreeProxy(rand=True).get_proxy_list()[:5])
# for i in range(2):
#     print(FreeProxy.get_first_working_proxy())