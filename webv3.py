#!/bin/python
from settings_file import *
from dermod import db
from dermod import input_parser as ip
from dermod import mime_types as mimes
from dermod import derpiload_v3 as derpiload
from dermod import derpilist_v2 as derpilist
import socket
from threading import Thread
from datetime import datetime
import os
import time


class ThreadController(Thread):
    
    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        j = ''
        for i in args:
            j += str(i)
        print(f"[DEBUG] @ [{t}] " + str(j))

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
                    del i
                    p = p + 1
            if p == 0:
                pass
            else:
                self.log_debug(f"Running threads {len(self.threads)} ({p} threads destroyed)")


class UDPHandler(Thread):

    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        j = ''
        for i in args:
            j += str(i)
        print(f"[DEBUG] @ [{t}] " + str(j))

    def __init__(self):
        Thread.__init__(self)
        self.port = 29888
        self.ip = '0.0.0.0'

    def start_listener(self):
        global web_port
        sock = socket.socket(socket.SOCK_DGRAM, socket.AF_INET, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        while True:
            h = sock.recv(1024)
            if h != b'':
                h = h.decode()
                host = h
                self.log_debug(f"[UDP] Received discovery from {socket.gethostbyname(host)} ({host})")
                h = str(socket.gethostbyname(socket.gethostname()))
                h = h + ":" + str(web_port)
                sock.sendto(h.encode(), (host, 29889))

    def run(self):
        self.start_listener()


class Handler(Thread):

    def __init__(self, csock, ip):
        Thread.__init__(self)
        self.conn = csock
        self.req = csock.recv(1024)
        self.ip = ip
        self.request = None
        self.readiness = 0

    def run(self):
        self.request = ip.request_parser(self.req)
        self.serve()
        self.readiness = 1

    def send_data(self, data):
        try:
            self.conn.send(data.encode())
        except AttributeError:
            self.conn.send(data)
        self.conn.close()

    def send_header(self, code, mime='html'):
        mime = mimes.types[mime]
        if code == 200:
            self.conn.sendall(f"HTTP/1.1 200 OK\nServer: PyWeb/3.0\nContent-Type: {mime}\n"
                              f"X-HTTP-Pony: I'm working hard for you\n\n".encode())
        elif code == 404:
            self.conn.sendall(f"HTTP/1.1 404 Not Found\nServer: PyWeb/3.0\nContent-Type: {mime}\n"
                              f"X-HTTP-Pony: Looks like i'm pretty awful in searching things\n\n".encode())
            self.send_data("<html>"
                           "<head>"
                           "<meta http-equiv='refresh' content='1; url=/' "
                           "</head>"
                           "<body>"
                           "404 Not Found"
                           "</body>"
                           "</html>")
            self.conn.close()
        elif code == 500:
            self.conn.sendall(f"HTTP/1.1 500 Internal Server Error\nServer: PyWeb/3.0\nContent-Type: "
                              f"{mime}\nX-HTTP-Pony: Well shit...\n\n".encode())
            self.send_data("500 Internal Server Error")
            self.conn.close()

    def log_request(self):
        request = self.request
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        print(f"[REQUEST] [{self.ip} @ {t}] Made request: {request['method']} {request['path'] } with params "
              f"'params: {request['params']}', 'query: {request['query']}'")

    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        for i in args:
            print(f"[DEBUG] @ [{t}] " + str(i))

    def serve(self):
        self.log_request()
        if self.request['path'] == '/' and self.request['query'] is None:
            self.send_header(200)
            self.send_data(open("extra/index.html", 'rb').read())
        elif self.request['path'].split('/')[1] == 'images' and self.request['path'].split('/')[2] is not '':
            try:
                f_type = self.request['path'].split('.')[-1]
                f = open(f"{images_path+self.request['path'].split('/')[-1]}", 'rb').read()
            except FileNotFoundError:
                self.send_header(404)
            else:
                self.send_header(200, f_type)
                self.send_data(f)
        elif self.request['path'] == '/export' and self.request['params']['id'] is not None:
            try:
                src_file = open(f"{images_path+self.request['params']['id']}", 'rb').read()
            except FileNotFoundError:
                self.send_header(404)
            else:
                try:
                    open(f"{export_path+self.request['params']['id']}", 'wb').write(src_file)
                except FileNotFoundError:
                    os.mkdir(export_path)
                    open(f"{export_path+self.request['params']['id']}", 'wb').write(src_file)
                except Exception:
                    self.send_header(500)
                else:
                    self.send_header(200)
                    self.send_data('Done')
        elif self.request['path'] == '/' and self.request['query'] is not None:
            try:
                s = datetime.now()
                results = list(sorted(db.search(self.request["query"]['search'],
                                                self.request["query"]['remove'])
                                      [int(self.request['params']['page'])-1]))
                n = datetime.now()
                self.log_debug("Query time: " + str(n-s))
            except Exception:
                self.send_header(404)
            else:
                pictures = []
                for i in results:
                    i = list([x for x in list(i) if x is not None])
                    i = tuple([x for x in i if x != 'None'])
                    pictures.append(i)
                p = ''
                for i in set(pictures):
                    if i[0].split('.')[1] != 'webm':
                        try:
                            p += f"""<div class='g-item'><abbr title="{str(i[1:-3]).strip('()').replace("'", '')}"><img src="
                        /images/{i[0]}" onclick="sclick('{i[0].split('.')[0]}')" class="img-fluid"></abbr></div>"""
                        except Exception:
                            self.send_header(500)
                    elif i[0].split('.')[1] == 'webm':
                        p += f"""<div class='g-item'><abbr title="{str(i[1:-3]).strip('()').replace("'", '')}">
                                 <video class="img-fluid" preload='auto' muted onclick="sclick('{i[0].split('.')[0]}')">
                                 <source src="{images_path}{i[0]}"/>
                                 </video>
                                 </abbr></div>"""
                try:
                    p = open("extra/results.html", 'r').read().format(self.request['params']['query'],
                                                                      p,
                                                                      int(self.request['params']['page']) - 1,
                                                                      self.request['params']['query'],
                                                                      int(self.request['params']['page']) + 1)
                except Exception:
                    self.send_header(500)
                else:
                    self.send_header(200)
                    self.send_data(p)
        elif self.request['path'] == '/update':
            self.send_header(200)
            self.send_data("started")
            derpilist.run()
            derpiload.run(ids_file)
            db.mkdb(table_name, columns, tag_amount)
            db.fill_db()
            print("DB configured successfully")
            os.remove(ids_file)
            print("Image index is up-to-date")
        elif "/image/" in self.request['path']:
            img_id = self.request['path'].split("/")[-1]
            tags = db.search_by_id(img_id)
            tags = [x for x in tags[0] if x is not None]
            if tags[0].split('.')[1] != 'webm':
                p = '<img src="/images/{}" class="img img-fluid">'.format(tags[0])
            else:
                p = f"""<video class="img img-fluid" preload='auto' autoplay controls muted loop>
                    <source src="/{images_path}{tags[0]}"/>
                    </video>"""
            data = open('extra/image.html', 'r').read().format(img_id, p, tags[0], tags[0],
                                                               str([f"<a href='/?query={f}&page=1'>{f}</a>"
                                                                    for f in [x for x in tags[1:-3]] if f != "None"])
                                                               .strip("[]").replace('"', ''))
            self.send_header(200)
            self.send_data(data)
        elif self.request['path'] == '/panic' or self.request['path'] == '/shutdown':
            self.send_header(200)
            self.send_data("Done")
            os._exit(0)
        elif self.request['path'] == '/dl' and 'id' in self.request['params']:
            try:
                with open(str(images_path+self.request['params']['id']), 'rb') as t:
                    temp = t.read()
            except FileNotFoundError:
                self.send_header(404)
            except Exception as e:
                print(e)
                self.send_header(500)
            else:
                self.send_header(200, self.request['params']['id'].split('.')[-1])
                self.send_data(temp)
                del temp
        elif self.request['path'] == '/raw' and 'id' in self.request['params']:
            try:
                temp = open(str(images_path+self.request['params']['id']), 'rb').read()
            except Exception:
                self.send_data(str(500))
            else:
                self.send_data(temp)
                del temp
        else:
            try:
                self.request['path'] = self.request['path'].replace('..', '')
                f_type = self.request['path'].split('.')[-1]
                data = open(os.curdir+self.request['path'], 'rb').read()
            except FileNotFoundError:
                self.send_header(404)
            except Exception:
                self.send_header(500)
            else:
                self.send_header(200, f_type)
                self.send_data(data)

try:
    print("Server started at http://{}:{}".format(web_ip, web_port))
    tc = ThreadController()
    tc.start()
    UDPsrv = UDPHandler()
    UDPsrv.start()
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((web_ip, web_port))
    sock.listen(10)
    while True:
        try:
            conn, addr = sock.accept()
            newT = Handler(conn, addr[0])
            newT.start()
            tc.threads.append(newT)
        except ConnectionResetError:
            pass
except KeyboardInterrupt:
    os._exit(0)
