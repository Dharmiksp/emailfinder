import requests
from bs4 import BeautifulSoup


def get_proxy():  # Get proxy ip and port and return array
    # create proxy library
    url = 'http://www.sslproxies.org/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # copy proxy list
    proxy_arr = (list(map(lambda x: x[0] + ":" + x[1], list(zip(map(lambda x: x.text, soup.findAll('td')[::8]),
                                                                map(lambda x: x.text, soup.findAll('td')[1::8])))))
                 )
    return proxy_arr