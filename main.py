import requests
import urllib.request


r = ("https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=489022")

request = urllib.request.Request(r,
                                  headers = { 'User-Agent': 'Mozilla/5.0'})

web = urllib.request.urlopen(request).read()



print(web)

