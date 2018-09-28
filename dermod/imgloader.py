import gc
import os
import socket
import sys
import time
from threading import Thread

import requests

import settings_file

from . import input_parser as ip
from . import threads as TC


class Loader(Thread):
    def __init__(self, url, fileid, fileform, is_proxy, proxy_ip, proxy_port):
        Thread.__init__(self)
        self.readiness = 0
        self.url = url
        self.id = fileid
        self.format = fileform
        self.raw_data = b''
        self.proxy = is_proxy
        self.ip = proxy_ip
        self.port = proxy_port
        if settings_file.suppressor is True:
            suppress = open(os.devnull, 'w')
            sys.stderr = suppress

    def run(self):
        self.get_raw_image()
        self.writer()
        self.readiness = 1
        del self.raw_data
        quit(0)

    def get_raw_image(self):
        if self.proxy is False:
            self.raw_data = requests.get(
                "{}".format(self.url), verify=settings_file.ssl_verify).content
        else:
            self.raw_data = requests.get(
                "{}".format(self.url),
                proxies=dict(https='socks5://{}:{}'.format(self.ip, self.port)), verify=settings_file.ssl_verify).content

    def writer(self):
        try:
            open(settings_file.images_path + self.id +
                 '.' + self.format, 'rb').close()
        except FileNotFoundError:
            with open(settings_file.images_path + self.id + '.' + self.format, 'wb') as file:
                file.write(self.raw_data)
                file.flush()


def run(file, check_files=True, check_local=True, endwith="\r"):
    tc = TC.ThreadController()
    tc.start()
    old_out = sys.stderr
    if settings_file.suppressor is True:
        suppress = open(os.devnull, 'w')
        sys.stderr = suppress
    try:
        os.mkdir(settings_file.images_path)
    except FileExistsError:
        pass
    parsed = ip.name_tag_parser(file)
    chk = len(parsed)
    print("Loading Images" + " " * 32, flush=True, end=endwith)
    c = 0
    if "PyPy" in sys.version:
        slp = 0.1
    else:
        slp = 0.2
    if check_files is True:
        for i in range(chk):
            print(
                "Loading image {} of {} ({}% done) (Running threads {})".format(
                    i, chk, format(((i/chk)*100), '.4g'), len(tc.threads)) + " " * 32,
                flush=True, end=endwith)
            try:
                open(settings_file.images_path +
                     str(parsed[i][7] + parsed[i][0]) + '.' + parsed[i][1], 'rb').close()
            except FileNotFoundError:
                t = Loader(parsed[i][2],
                           str(parsed[i][7] + parsed[i][0]),
                           parsed[i][1],
                           settings_file.enable_proxy,
                           settings_file.socks5_proxy_ip,
                           settings_file.socks5_proxy_port)
                t.start()
                tc.threads.append(t)
                time.sleep(slp)
                if len(tc.threads) < settings_file.thread_cap:
                    pass
                else:
                    time.sleep(settings_file.sleep_time)
    else:
        for i in range(chk):
            print(
                "Loading image {} of {} ({}% done) (Running threads {})".format(
                    i, chk, format(((i/chk)*100), '.4g'), len(tc.threads)) + " " * 32,
                flush=True, end=endwith)
            t = Loader(parsed[i][2],
                       str(parsed[i][7] + parsed[i][0]),
                       parsed[i][1],
                       settings_file.enable_proxy,
                       settings_file.socks5_proxy_ip,
                       settings_file.socks5_proxy_port)
            t.start()
            tc.threads.append(t)
            time.sleep(slp)
            if len(tc.threads) < settings_file.thread_cap:
                pass
            else:
                time.sleep(settings_file.sleep_time)
    while len(tc.threads) > 0:
        gc.collect()
        print("Waiting {} thread(s) to end routine".format(
            len(tc.threads)) + " " * 32, flush=True, end=endwith)
        if c >= settings_file.time_wait and len(tc.threads) < 5:
            tc.threads = []
        elif len(tc.threads) < 5:
            print("Left to download {}".format(str([x.id for x in [x for x in tc.threads]]))+ " "*32, end=endwith)
            time.sleep(1)
            c += 1
    del tc
    sys.stderr = old_out
