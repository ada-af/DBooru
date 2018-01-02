import gc
import os
import re
import shutil
import sys
import time
import importlib
from threading import Thread

import requests

import settings_file
from dermod import threads as TC
from dermod import input_parser as ip


class Checker(Thread):
    def __init__(self, page, module, proxy_ip, proxy_port, proxy_enabled):
        Thread.__init__(self)
        self.page = page
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_enabled = proxy_enabled
        self.module_data = module.Module
        self.module = module
        self.raw_data = ''
        self.compiled = ''
        self.readiness = 0

    def get_data(self):
        if self.proxy_enabled is False:
            with requests.Session() as s:
                s.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
                self.raw_data = s.get(
                    "{domain}{endpoint}{params}&{paginator}".format(domain=self.module.domain,
                    endpoint=self.module.endpoint,
                    params=self.module.params,
                    paginator=self.module.paginator.format(self.page)),
                    verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
            self.raw_data = self.raw_data.content.decode()
        else:
            with requests.Session() as s:
                s.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
                self.raw_data = s.get(
                    "{domain}{endpoint}{params}&{paginator}".format(domain=self.module.domain,
                    endpoint=self.module.endpoint,
                    params=self.module.params,
                    paginator=self.module.paginator.format(self.page)),
                proxies=dict(https='socks5://{}:{}'.format(self.proxy_ip, self.proxy_port)),
                verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
            self.raw_data = self.raw_data.content.decode()

    def parse_data(self):
        self.module_data.parse(self, string=self.raw_data)

    def compile(self):
        for i in range(0, len(self.ids)):
            tmp = str(str(self.ids[i] + ",,," +
                          self.form[i] + ",,," +
                          self.links[i] + ",,," +
                          self.width[i] + ",,," +
                          self.height[i] + ",,," +
                          str(int(self.width[i])/int(self.height[i])) + ",,," +
                          self.tags[i]).encode("utf8", errors='ignore'))[2:-1] + "\n"
            self.compiled += tmp

    def writer(self):
        with open('tmp/{}.txt'.format(self.page), 'w+') as f:
            f.write(self.compiled)
            f.flush()
            len(f.read())

    def run(self):
        self.get_data()
        if re.match("{}".format(self.module.empty_page), self.raw_data) is not None:
            global empties
            empties = 1
        self.parse_data()
        self.compile()
        self.writer()
        with open('tmp/{}.txt'.format(self.page), 'r') as f:
            tmp = f.read()
        if len(tmp) == 0 and re.match("{}".format(self.module.empty_page), self.raw_data) is None:
            self.run()
        self.readiness = 1
        quit()


def run(module, follower=False, pages_num=0, file=settings_file.ids_file):
    global empties
    empties = 0
    print("Searching for max page")
    pages_num = 0
    if follower is True:
        pass
    else:
        pages_num = 0
        k = False
        while k is False:
            pages_num += 50
            print('\rFinding max page... (Checking Page {})'.format(pages_num), flush=True, end='')
            dat = requests.get(
                "{domain}{endpoint}{params}&{paginator}".format(domain=module.domain,
                endpoint=module.endpoint,
                params=module.params,
                paginator=module.paginator.format(pages_num)),
                verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
            if type(re.match("{}".format(module.empty_page), dat.content.decode())) is not None:
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
    tc = TC.ThreadController()
    tc.start()
    try:
        slp = module.slp
    except Exception:
        if "PyPy" in sys.version:
            slp = 0.1
        else:
            slp = 0.2
    for i in range(pages_num+1):
        gc.collect()
        print("\rChecking page {} of {} ({}% done)(Running threads {})          ".format(i, pages_num, format(((i/pages_num)*100), '.4g'), len(tc.threads)), flush=True, end='')
        t = Checker(page=i, proxy_ip=settings_file.socks5_proxy_ip, proxy_port=settings_file.socks5_proxy_port, proxy_enabled=settings_file.enable_proxy, module=module)
        t.start()
        tc.threads.append(t)
        if empties == 1:
            break
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
    with open(file, 'w') as f:
        for i in range(pages_num):
            print("\rProcessing file {}.txt  ".format(i), end='', flush=True)
            try:
                with open('tmp/{}.txt'.format(i), 'r') as tmp:
                    f.write(tmp.read())
                f.flush()
                time.sleep(0.01)
            except FileNotFoundError:
                pass