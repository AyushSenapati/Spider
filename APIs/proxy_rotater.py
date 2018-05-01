#! /usr/bin/env python3

import requests
from itertools import cycle
from .getProxy import proxy_pool

def update_proxy_pool():
    # Get list of available proxies online
    print('Fetching proxy list from the web...')
    proxy_pool.update_proxy_pool()
    print('Filtering elite proxies having https support...')
    # Create a proxy pool from the available proxy list
    proxies = proxy_pool.get_pool()
    pool = cycle(proxies)
    print('Proxy pool has been created.')
    return pool

def main():
    url = 'https://httpbin.org/ip'
    pool = update_proxy_pool()
    for i in range(1, 11):
        proxy = next(pool)
        print(f"Request #{i}")
        try:
            resp = requests.get(url, timeout=5, proxies={'https': proxy})
            print(resp.json())
        except ConnectionError as e:
            print(e)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()

