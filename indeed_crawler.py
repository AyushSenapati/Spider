#! /usr/bin/env python3

import urllib.parse
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from random import randint
from time import sleep
from datetime import datetime
import threading

from APIs.proxy_rotater import update_proxy_pool


class Crawler(object):
    main_url = 'https://www.indeed.com'
    def __init__(self):
        self.index = 1

    def crawl(self, querry, nxt_page=None, proxy='', qid=''):
        """
        Responsible for crawling pages
        and parsing them using BeautifulSoup
        """
        if qid:
            qid = '(Thread-' + str(qid) + ')'
        retry = 3
        url = self.main_url + '/jobs?' + querry
        if nxt_page:
            url = nxt_page
        print(f'{qid}\tURL: {url}')
        s_time = datetime.now()
        resp = requests.get(url, timeout=10, proxies={'https': proxy})
        while (resp.status_code != 200) and (retry > 0):
            retry -= 1
            print(f"{qid} INFO: Retry left: {retry}")
            timeout += 5
            print(f'{qid} INFO: retrying...')
            sleep(randint(3,15))
            resp = requests.get(url, timeout=timeout, proxies={'https': proxy})
            print(resp)
        soup = bs(resp.text, 'html.parser')
        print(f'{qid}\tCrawled in ---{datetime.now() - s_time} sec---')
        return soup

    def get_data(self, soup, qid=''):
        if qid:
            qid = '(Thread-' + str(qid) + ')'
        s_time = datetime.now()
        db = {}
        print(f'{qid}\tExtracting items...')
        searched_list = soup.find_all('td', id='resultsCol')[0].find_all('div', class_='row')
        
        # Fetch all the items listed in the webpage
        for item in searched_list:
            db[self.index] = {'title': item.find(class_='jobtitle').find('a')['title'],
                        'link': self.main_url + item.find(class_='jobtitle').find('a')['href'],
                        'company': item.find(class_='company').text.strip('\n').strip(' '),
                        'location': item.find(class_='location').text.strip('\n').strip(' '),
                        'date': item.find(class_='date').text.strip('\n').strip(' ')
                        }
            # Handle jobs with no salary mentioned
            if item.find(class_='no-wrap'):
                db[self.index]['salary'] = item.find(class_='no-wrap').text.strip('\n').strip(' ')
            else:
                db[self.index]['salary'] = '-NA-'
            if item.find(class_='slNoUnderline'):
                db[self.index]['reviews'] = item.find(class_='slNoUnderline').text.strip('\n').strip(' ')
            else:
                db[self.index]['reviews'] = '-NA-'
            self.index += 1
        
        #print(db)
        try:
            nxt_page = self.main_url + soup.find(class_='pagination').find_all('a')[-1]['href']
        except AttributeError:
            nxt_page = None
            print(f'{qid} Error in finding next page...')
        print(f'{qid}\tData extracted in ---{datetime.now() - s_time} sec---')
        return (db, nxt_page)


def run(crawler, q_id, proxy, depth, querry):
    global db
    lock = threading.Lock()
    # Perform crawling at random interval
    cur_depth = 0
    depth_limit = depth
    sleep(randint(3,15))
    print(f"(Thread-{q_id}) {q_id}# Crawling depth-{cur_depth}:")
    soup = crawler.crawl(querry, qid=q_id)
    tmp_db, nxt_page = crawler.get_data(soup, qid=q_id)
    if not nxt_page:
        depth_limit = 0
    print(f'(Thread-{q_id}) Waiting for the lock to be acquired..')
    lock.acquire()
    try:
        db.update(tmp_db)
    finally:
        lock.release()
        print(f'(Thread-{q_id}) Lock has been released.')
    while depth_limit:
        cur_depth += 1
        print(f"(Thread-{q_id})  * Crawling depth-{cur_depth}:")
        soup = crawler.crawl(nxt_page, qid=q_id)
        tmp_db, nxt_page = crawler.get_data(soup, qid=q_id)
        # print(f"##########{nxt_page}################")
        depth_limit -= 1
        lock.acquire()
        try:
            db.update(tmp_db)
        finally:
            lock.release()
        if not nxt_page:
            depth_limit = 0

db = {}
def main():
    try:
        depth = int(input('Enter depth limit >> '))
    except ValueError:
        print('A valid depth was expected..\nSetting default depth to 3')
        depth = 3
    print(f'Depth has been set to {depth}')
    #db = {}
    crawler = Crawler()
    # create file object
    with open('test_files/job_keywords.csv') as j_obj:
        jobs = j_obj.read().split('\n')
        jobs.pop(-1)
    with open('test_files/locations.csv') as loc_obj:
        locations = loc_obj.read().split('\n')
        locations.pop(-1)

    # Querry generator
    querry_generator = (urllib.parse.urlencode({'q': job, 'l': loc}) for job in jobs for loc in locations)
    
    # Update proxies
    pool = update_proxy_pool()

    q_id = 1
    thread_pool = []
    try:
        # Start generating querries from the generator
        for querry in querry_generator:
            proxy = next(pool)
            # Start new thread for each new querry
            t_obj = threading.Thread(target=run, args=(crawler, q_id, proxy, depth, querry))
            print(f"{t_obj.name} is using {proxy}")
            t_obj.start()
            thread_pool.append(t_obj)
            q_id += 1
        print(f'Threads in the pool:\n{thread_pool}')
        print('Wating for all threads to exit...')
        for thread in thread_pool:
            thread.join()
        print('No more querries found.')
        print('Crawling completed.')
    except KeyboardInterrupt:
        print('Crawler has been terminated!!')
    except Exception as e:
        raise(e)
    finally:
        if db:
            f_name = '/tmp/indeed.json'
            df = pd.DataFrame.from_dict(db, orient='index')
            df.to_json(f_name)
            print(f'DataFrame has been dumped to {f_name}')
            opt = input('Shall I display the prepared dataframe? (yes/no): ')
            if opt in ('yes', 'y'):
                print(df)
        else:
            print('data frame has not been initialized')

if __name__ == '__main__':
    print('Initializing the Crawler...')
    main()

