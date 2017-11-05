import gc
import os
import re
import shutil
import sys
import time
from threading import Thread

import requests

from settings_file import *


class Error(Exception):
    pass


class Timeouted(Error):
    def __init__(self):
        pass


class Timer(Thread):
    def __init__(self, to):
        Thread.__init__(self)
        self.time = to
        self.done = 0

    def run(self):
        time.sleep(self.time)
        if self.done == 0:
            raise Timeouted
        else:
            pass

    def stop(self):
        self.done = 1


class ThreadController(Thread):
    @staticmethod
    def log_debug(*args):
        j = ''
        for i in args:
            j += str(i)
        print("[DEBUG] " + str(j))

    def __init__(self):
        Thread.__init__(self)
        self.threads = []

    def run(self):
        self.watcher()

    def watcher(self):
        while True:
            time.sleep(1)
            p = 0
            for i in self.threads:
                if i.readiness == 1:
                    self.threads.remove(i)
                    i.join()
                    del i
                    p = p + 1


class Checker(Thread):

    def __init__(self, all_pages, page, is_proxy, api_key, vote, proxy_ip, proxy_port):
        global suppressor, domain
        Thread.__init__(self)
        self.domain = domain
        self.readiness = 0
        self.compiled = ''
        self.pages = all_pages
        self.raw_data = ''
        self.tags = []
        self.ids = []
        self.links = []
        self.form = []
        self.height = []
        self.width = []
        self.ratio = []
        self.page = page
        self.proxy = is_proxy
        self.api_key = api_key
        self.vote = vote
        self.ip = proxy_ip
        self.port = proxy_port
        if suppressor is True:
            suppress = open(os.devnull, 'w')
            sys.stderr = suppress

    def get_data(self):
        if self.proxy is False:
            self.raw_data = requests.get(
                "https://{}/search.json/?q=my:{}".format(self.domain, self.vote) +
                "&page={}".format(self.page) +
                "&key={}".format(self.api_key), verify=ssl_verify, timeout=10)
            self.raw_data = self.raw_data.content.decode()
        else:
            self.raw_data = requests.get(
                "https://{}/search.json/?q=my:{}".format(self.domain, self.vote) +
                "&page={}".format(self.page) +
                "&key={}".format(self.api_key),
                proxies=dict(https='socks5://{}:{}'.format(self.ip, self.port)), verify=ssl_verify, timeout=10)
            self.raw_data = self.raw_data.content.decode()

    def parse_data(self):
        string = self.raw_data.replace("'", '"')
        string = string.split('"id":"')[1:]
        ids = []
        form = []
        links = []
        tags = []
        height = []
        width = []
        ratio = []
        for i in string:
            k = i.split('"width":')[1]
            k = k.split(',')[0]
            width.append(k)
            k = i.split('"height":')[1]
            k = k.split(',')[0]
            height.append(k)
            k = i.split('"aspect_ratio":')[1]
            k = k.split(',')[0][:10]
            ratio.append(k)
            ids.append(i.split('","')[0])
            k = i.split('original_format')[1]
            k = k.split('":"')[1].split('","')[0]
            form.append(k)
            k = i.split('","large":"')[1]
            k = k.split('","tall"')[0]
            links.append(k)
            tags.append(i.split('"tags":"')[1].split('"')[0])
        self.ids = ids
        self.form = form
        self.links = links
        self.tags = tags
        self.height = height
        self.width = width
        self.ratio = ratio

    def compile(self):
        for i in range(0, len(self.ids)):
            tmp = str(str(self.ids[i] + ",,," +
                      self.form[i] + ",,," +
                      self.links[i] + ",,," +
                      self.width[i] + ",,," +
                      self.height[i] + ",,," +
                      self.ratio[i] + ",,," +
                      self.tags[i]).encode("utf8", errors='ignore'))[2:-1] + "\n"
            self.compiled += tmp

    def writer(self):
        with open('tmp/{}.txt'.format(self.page), 'w+') as f:
            f.write(self.compiled)
            f.flush()
            len(f.read())

    def run(self):
        timer = Timer(time_wait)
        try:
            timer.start()
            self.get_data()
            timer.stop()
        except Exception:
            pass
        self.parse_data()
        self.compile()
        self.writer()
        with open('tmp/{}.txt'.format(self.page), 'r') as f:
            tmp = f.read()
        if len(tmp) == 0 and re.match('{"search":\[\]', self.raw_data).group() != '{"search":[]':
            self.run()
        else:
            pass
        self.readiness = 1


def run():
    global user_api_key, vote, enable_proxy, socks5_proxy_ip, socks5_proxy_port, suppressor, ids_file, domain
    if suppressor is True:
        suppress = open(os.devnull, 'w')
        sys.stderr = suppress
    pages_num = 0
    k = False
    while k is False:
        pages_num += 50
        print('\rFinding max page... (Checking Page {})'.format(pages_num), flush=True, end='')
        dat = requests.get(
            "https://{}/search.json/?q=my:{}&page={}&filter_id=56027&key={}".format(
                domain,
                vote,
                pages_num,
                user_api_key), verify=ssl_verify, timeout=10)
        if re.match('{"search":\[\]', dat.content.decode()) is not None:
            k = True
    k = False
    while k is False:
        try:
            os.mkdir("tmp")
            k = True
        except Exception:
            try:
                shutil.rmtree('tmp')
            except Exception:
                pass
    tc = ThreadController()
    tc.start()
    if "PyPy" in sys.version:
        slp = 0.1
    else:
        slp = 0.2
    for i in range(pages_num+1):
        gc.collect()
        print("\rChecking page {} of {} ({}% done)(Running threads {})          ".format(i, pages_num, format(((i/pages_num)*100), '.4g'), len(tc.threads)), flush=True, end='')
        t = Checker(pages_num, i, enable_proxy, user_api_key, vote, socks5_proxy_ip, socks5_proxy_port)
        t.start()
        tc.threads.append(t)
        time.sleep(slp)
    c = 0
    while len(tc.threads) > 0:
        gc.collect()
        print("\rWaiting {} thread(s) to end routine".format(len(tc.threads)) + " "*16, flush=True, end='')
        if c >= 5 and len(tc.threads) < 10:
            tc.threads = []
        else:
            time.sleep(1)
            c += 1
    del tc
    print("Concatenating files...")
    with open(ids_file, 'w') as f:
        for i in range(pages_num+1):
            print("\rProcessing file {}.txt  ".format(i), end='', flush=True)
            with open('tmp/{}.txt'.format(i), 'r') as tmp:
                f.write(tmp.read())
            f.flush()
            time.sleep(0.01)
