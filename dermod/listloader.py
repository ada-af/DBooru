import gc
import importlib
import os
import re
import shutil
import sys
import time
from hashlib import sha384
from threading import Thread

import requests

import settings_file
from dermod import input_parser as ip
from dermod import threads as TC

global is_error_code
is_error_code = False

class Checker(Thread):
    def __init__(self, page, module, proxy_ip, proxy_port, proxy_enabled):
        Thread.__init__(self)
        self.page = page
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_enabled = proxy_enabled
        self.module_data = module.Module()
        self.module = module
        self.raw_data = ''
        self.compiled = ''
        self.readiness = 0

    def get_data(self):
        global is_error_code
        with requests.Session() as s:
            if is_error_code is True:
                quit(1)
            s.headers = {
                'User-Agent': 'DBooru/2.0 (Api checker module)(github.com/mcilya/DBooru)'}
            if self.proxy_enabled is False:
                self.raw_data = s.get(
                    "{domain}{endpoint}{paginator}{params}".format(domain=self.module.domain,
                                                                   endpoint=self.module.endpoint,
                                                                   params=self.module.params,
                                                                   paginator=self.module.paginator.format(self.page)),
                    verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
            else:
                self.raw_data = s.get(
                    "{domain}{endpoint}{paginator}{params}".format(domain=self.module.domain,
                                                                   endpoint=self.module.endpoint,
                                                                   params=self.module.params,
                                                                   paginator=self.module.paginator.format(self.page)),
                    proxies=dict(
                        https='socks5://{}:{}'.format(self.proxy_ip, self.proxy_port)),
                    verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
        if self.raw_data.status_code >= 400:
            is_error_code = True
        try:
            self.raw_data = self.raw_data.content.decode("unicode_escape")
        except UnicodeEncodeError:
            self.raw_data = self.raw_data.content.decode()

    def parse_data(self):
        self.module_data.parse(string=self.raw_data, pg_num=self.page)

    def compile(self):
        digest = str(sha384(self.module.__name__.encode()).hexdigest())[
            :6] + "_"
        for i in range(0, len(self.module_data.ids)):
            try:
                tmp = str(str(self.module_data.ids[i] + ",,," +
                          self.module_data.form[i] + ",,," +
                          self.module_data.links[i] + ",,," +
                          self.module_data.width[i] + ",,," +
                          self.module_data.height[i] + ",,," +
                          str(int(self.module_data.width[i])/int(self.module_data.height[i])) + ",,," +
                          ",," + self.module.__name__.split(".")[-1] + ',,' + self.module_data.tags[i] + ",,," +
                          digest).encode("utf8", 'strict'))[2:-1] + "\n"
                self.compiled += tmp
            except IndexError:
                pass

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
            global is_error_code
            if is_error_code == False:
                self.run()
        self.readiness = 1
        quit()


def run(module, follower=False, pages_num=0, file=settings_file.ids_file, endwith="\r"):
    global empties
    empties = 0
    print("Searching for max page")
    try:
        hard_limit = module.hard_limit
    except Exception:
        pass
    pages_num = 50
    if follower is True:
        pass
    else:
        pages_num = 1
        k = False
        while k is False:
            pages_num += 50
            print('Finding max page... (Checking Page {})'.format(
                pages_num-1), flush=True, end=endwith)
            with requests.Session() as s:
                s.headers = {
                    'User-Agent': 'DBooru/2.0 (Api checker module)(github.com/mcilya/DBooru)'}
                dat = s.get(
                    "{domain}{endpoint}{paginator}{params}".format(domain=module.domain,
                                                                   endpoint=module.endpoint,
                                                                   params=module.params,
                                                                   paginator=module.paginator.format(pages_num)),
                    verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
            if dat.status_code >= 400:
                break
            if re.search("{}".format(module.empty_page), dat.content.decode()) is not None:
                k = True
            try:
                if pages_num >= hard_limit:
                    k = True
                    pages_num = hard_limit
                    break
            except UnboundLocalError:
                pass
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
    if "PyPy" in sys.version:
        slp = 0.1
    else:
        slp = 0.2
    for i in range(1, pages_num+1):
        gc.collect()
        print("Checking page {} of {} ({}% done)(Running threads {})          ".format(
            i, pages_num, format(((i/pages_num)*100), '.4g'), len(tc.threads)), flush=True, end=endwith)
        if is_error_code is True:
            break
        t = Checker(page=i,
                    proxy_ip=settings_file.socks5_proxy_ip,
                    proxy_port=settings_file.socks5_proxy_port,
                    proxy_enabled=settings_file.enable_proxy,
                    module=module)
        t.start()
        tc.threads.append(t)
        if empties == 1:
            break
        time.sleep(module.slp)
    c = 0
    while len(tc.threads) > 0:
        gc.collect()
        print("Waiting {} thread(s) to end routine".format(
            len(tc.threads)) + " " * 32, flush=True, end=endwith)
        if c >= 15 and len(tc.threads) < 10:
            tc.threads = []
        else:
            time.sleep(1)
            c += 1
    del tc
    print("\rConcatenating files..."+" "*32)
    with open(file, 'w') as f:
        for i in range(pages_num):
            print("Processing file {}.txt  ".format(i), end=endwith, flush=True)
            try:
                with open('tmp/{}.txt'.format(i), 'r') as tmp:
                    f.write(tmp.read())
                f.flush()
                time.sleep(0.01)
            except FileNotFoundError:
                pass
