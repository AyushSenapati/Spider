#! /usr/bin/env python3

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

class Proxy(object):
    """
    API to get proxy list from [free-proxy-list.net].
    This API may to work correctly if the design of the website
    gets changed over time.
    """
    def __init__(self):
        self.url = 'https://free-proxy-list.net/'
        self._data_frame = None

    @property
    def data_frame(self):
        return self._data_frame

    @data_frame.setter
    def data_frame(self, value):
        print('Error: Altering data frame is not permitted')

    def update_proxy_pool(self):
        """
        Responsible for updating proxy data frame upon request.
        """
        proxy_list = []
        try:
            resp = requests.get(self.url)
        except ConnectionError as ce:
            print(ce)
            return(1)
        soup = bs(resp.text, "html.parser")
        proxy_table = soup.find_all(id='proxylisttable')
        for tr in proxy_table[0].find_all('tbody')[0].find_all('tr'):
            td = tr.find_all('td')
            proxy_list.append({
                'ip': td[0].text,
                'port': td[1].text,
                'anonymity': td[4].text.upper(),
                'https': td[6].text
                })
        self._data_frame = pd.DataFrame(proxy_list)

    def get_pool(self, **kwargs) -> type(set):
        """Returns a set() object containing
        filtered proxy pool as per the request.
        :para anonymity = ['elite proxy', 'anonymous', 'transparent']
        :para https = ['yes', 'no']
        """
        anonymity = kwargs.get('anonymity', 'elite proxy').upper()
        https = kwargs.get('https', 'yes')
        proxy_pool = set()
        # Filter proxy pool as per anonymity or https requirements
        filtered = self.data_frame[
                (self.data_frame['anonymity'] == anonymity)
                & (self.data_frame['https'] == https)
                ]
        for ip, port in zip(filtered['ip'], filtered['port']):
            proxy_pool.add(f"{ip}:{port}")
        return proxy_pool

proxy_pool = Proxy()

