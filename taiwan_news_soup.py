import io
import re
import json
import logging
import logging.config
from datetime import datetime

import requests
from bs4 import BeautifulSoup

def soup_from_url(url):
    soup = None
    resp = requests.get(url)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'lxml')
    return soup

def soup_from_file(file_path):
    soup = None
    with open(file_path, 'r') as cache_file:
        html = cache_file.read()
        soup = BeautifulSoup(html, 'lxml')
    return soup

def unicode_escape(s):
    e = ''
    for c in s:
        code = ord(c)
        if ord(c) < 128:
            e += c
        else:
            e += '\\u{:4x}'.format(code)
    return e

def scan_author(article):
    patterns = [
        '（(.{2,5})／.+報導）',
        '記者(.{2,5})／.+報導'
    ]
    for p in patterns:
        po = re.compile(p)
        m = po.search(article)
        if m is not None:
            return m[1]

def load_soup_conf():
    conf = None
    with open('conf/news-soup.json', 'r') as conf_file:
        conf = json.load(conf_file)
    del conf['what\'s that']
    return conf

class NewsSoup:

    def __init__(self, path):
        self.soup = None
        self.conf = None
        self.channel = 'unknown'
        self.cache = {
            'title': None,
            'date': None,
            'author': None,
            'contents': None,
            'tags': None
        }

        if path.startswith('https'):
            logger.debug('從網站載入新聞.')
            try:
                self.soup = soup_from_url(path)
            except:
                logger.error('無法載入新聞')
            all_conf = load_soup_conf()
            for (channel, conf) in all_conf.items():
                if channel in path:
                    self.channel = channel
                    self.conf = conf
        else:
            logger.debug('從檔案載入新聞.')
            try:
                self.soup = soup_from_file(path)
            except:
                logger.error('無法載入新聞')
            all_conf = load_soup_conf()
            for (channel, conf) in all_conf.items():
                if channel in path:
                    self.channel = channel
                    self.conf = conf

        if self.channel is None:
            if self.soup is None:
                logger.error('無法轉換 BeautifulSoup，可能是網址或檔案路徑錯誤')
            else:
                logger.error('不支援的新聞台，請檢查設定檔')

    def title(self):
        if self.cache['title'] is None:
            nsel = self.conf['desktop']['title_node']
            attr = self.conf['desktop']['title_attr']
            found = self.soup.select(nsel)
            if len(found) > 0:
                node = found[0]
                if attr != '':
                    self.cache['title'] = node[attr]
                else:
                    self.cache['title'] = node.text.strip()
                if len(found) > 1:
                    logger.warn('Found more than one title of channel [{}].'.format(self.channel))
            else:
                logger.error('Cannot find title of channel [{}].'.format(self.channel))
        else:
            print('title 已經有快取')
        return self.cache['title']

    def date(self):
        if self.cache['date'] is None:
            nsel = self.conf['desktop']['date_node']
            dfmt = self.conf['desktop']['date_format']
            found = self.soup.select(nsel)
            if len(found) > 0:
                node = found[0]
                # ettoday 的日期有換行字元，要先過濾再跑 strptime
                # TODO: 處理 parsing 例外
                self.cache['date'] = datetime.strptime(node.text.strip(), dfmt)
                if len(found) > 1:
                    logger.warn('Found more than one date of channel [{}].'.format(self.channel))
            else:
                logger.error('Cannot find date of channel [{}].'.format(self.channel))
        return self.cache['date']

    def author(self):
        if self.cache['author'] is None:
            nsel = self.conf['desktop']['author_node']
            if nsel != '':
                found = self.soup.select(nsel)
                if len(found) > 0:
                    node = found[0]
                    self.cache['author'] = node.text
                    if len(found) > 1:
                        logger.warn('Found more than one author of channel [{}].'.format(self.channel))
                else:
                    logger.error('Cannot find author of channel [{}].'.format(self.channel))
            else:
                contents = self.contents()
                if contents is not None:
                    self.cache['author'] = scan_author(contents)
                else:
                    logger.error('Cannot find author from contents of channel [{}].'.format(self.channel))
        return self.cache['author']

    def contents(self):
        if self.cache['contents'] is None:
            nsel = self.conf['desktop']['article_node']
            found = self.soup.select(nsel)
            if len(found) > 0:
                contents = io.StringIO()
                for node in found:
                    contents.write(node.text)
                self.cache['contents'] = contents.getvalue()
                contents.close()
            else:
                print(nsel)
                logger.error('Cannot find contents of channel [{}].'.format(self.channel))
        return self.cache['contents']

def main():
    samples = [
        # 測試快取
        'samples/appledaily.html',
        #'samples/cna.html',
        #'samples/ettoday.html',
        #'samples/judicial.html',
        #'samples/ltn.html',
        #'samples/on.html'
        #'samples/setn.html',
        #'samples/udn.html',
        # 測試實際頁面
        'http://tw.news.appledaily.com/local/realtime/20181025/1453825/',
        #'https://www.cna.com.tw/news/asoc/201810170077.aspx'
    ]

    print('-' * 80)
    for path in samples:
        ns = NewsSoup(path)
        print('頻道: ', end='')
        print(ns.channel)
        print('標題: ', end='')
        print(ns.title())
        print('日期: ', end='')
        print(ns.date())
        print('記者: ', end='')
        print(ns.author())
        print('內文:')
        print(ns.contents())
        print('-' * 80)

logging.config.fileConfig('conf/logging.ini')
logger = logging.getLogger()

if __name__ == '__main__':
    main()
