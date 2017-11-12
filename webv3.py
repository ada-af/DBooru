#!python
import os
import socket
import time
import sys
from datetime import datetime
from threading import Thread

from dermod import input_parser as ip
from dermod import mime_types as mimes
from dermod import db, predict, follow
import settings_file


class ThreadController(Thread):
    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        j = ''
        for i in args:
            j += str(i)
        print("[DEBUG] @ [{}] ".format(t) + str(j))

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
                self.log_debug("Running threads {} ({} threads destroyed)".format(len(self.threads), p))


class UDPHandler(Thread):
    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        j = ''
        for i in args:
            j += str(i)
        print("[DEBUG] @ [{}] ".format(t) + str(j))

    def __init__(self):
        Thread.__init__(self)
        self.port = 29888
        self.ip = '0.0.0.0'

    def start_listener(self):
        sock = socket.socket(socket.SOCK_DGRAM, socket.AF_INET, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        while True:
            h = sock.recv(1024)
            if h != b'':
                h = h.decode()
                host = h
                try:
                    self.log_debug("[UDP] Received discovery from {} ({})".format(socket.gethostbyname(host), host))
                except Exception:
                    self.log_debug("[UDP] Received discovery from '' ({})".format(host))
                h = str(socket.gethostbyname(socket.gethostname()))
                h = h + ":" + str(settings_file.web_port)
                sock.sendto(h.encode(), (host, 29889))

    def run(self):
        self.start_listener()


class Handler(Thread):

    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        for i in args:
            print("[DEBUG] @ [{}] ".format(t) + str(i))

    def __init__(self, csock, ip):
        Thread.__init__(self)
        self.conn = csock
        self.req = csock.recv(1024)
        self.ip = ip
        self.request = None
        self.readiness = 0

    def run(self):
        try:
            self.request = ip.request_parser(self.req)
            self.serve()
        except Exception:
            pass
        self.readiness = 1
        quit(0)

    def send_data(self, data):
        try:
            self.conn.send(data.encode())
        except AttributeError:
            self.conn.send(data)
        self.conn.close()

    def send_header(self, code, mime='html'):
        mime = mimes.types[mime]
        if code == 200:
            self.conn.sendall("""HTTP/1.1 200 OK\nServer: PyWeb/3.0\nContent-Type: {}\nX-HTTP-Pony: I'm working hard for you\n\n""".format(mime).encode())
        elif code == 404:
            self.conn.sendall("""HTTP/1.1 404 Not Found\nServer: PyWeb/3.0\nContent-Type: {}\nX-HTTP-Pony: Looks like i'm pretty awful in searching things\n\n""".format(mime).encode())
            self.send_data("<html><head><meta http-equiv='refresh' content='1; url=/' </head><body>404 Not Found</body></html>".encode())
        elif code == 500:
            self.conn.sendall("""HTTP/1.1 500 Internal Server Error\nServer: PyWeb/3.0\nContent-Type: {}\nX-HTTP-Pony: Well shit...\n\n""".format(mime).encode())
            self.send_data("500 Internal Server Error")
            self.conn.close()

    def log_request(self):
        request = self.request
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        print("""[REQUEST] [{} @ {}] Made request: {} {} with params {{'params: {}', 'query: {}'}}""" \
              .format(self.ip, t, request['method'], request['path'], request['params'], request['query']))

    def index(self):
        with open("extra/index.html", 'rb') as j:
            self.send_header(200)
            self.send_data(j.read())

    def show_img(self):
        try:
            f_type = self.request['path'].split('.')[-1]
            with open("{}".format(settings_file.images_path + self.request['path'].split('/')[-1]), 'rb') as j:
                f = j.read()
        except FileNotFoundError:
            self.send_header(404)
        else:
            self.send_header(200, f_type)
            self.send_data(f)

    def exporter(self):
        try:
            src_file = open(str(settings_file.images_path + self.request['params']['id']), 'rb').read()
        except FileNotFoundError:
            self.send_header(404)
        else:
            try:
                open(str(settings_file.export_path + self.request['params']['id']), 'wb').write(src_file)
            except FileNotFoundError:
                os.mkdir(settings_file.export_path)
                open(str(settings_file.export_path + self.request['params']['id']), 'wb').write(src_file)
            except Exception:
                self.send_header(500)
            else:
                self.send_header(200)
                self.send_data('Done')

    def results(self):
        try:
            results = list(db.search(self.request["query"]['search'],
                                     self.request["query"]['remove'])
                           [int(self.request['params']['page']) - 1])
        except (IndexError, KeyError):
            self.send_header(404)
        except Exception:
            self.send_header(500)
        else:
            pictures = []
            for i in results:
                i = list([x for x in list(i) if x is not None])
                i = tuple([x for x in i if x != 'None'])
                pictures.append(i)
            p = ''
            for i in sorted(list(set(pictures)), key=lambda tup: tup[0], reverse=True):
                if i[0].split('.')[1] != 'webm':
                    try:
                        p += """<div class="cont"><div class='g-item'><abbr title="{}"><img src="
                    /images/{}" onclick="sclick('{}')" class="img-fluid g-item"></abbr></div></div>""" \
                            .format(str(i[1:-3]).strip('()').replace("'", ''), i[0], i[0].split('.')[0])
                    except Exception:
                        self.send_header(500)
                elif i[0].split('.')[1] == 'webm':
                    p += """<div class="cont"><div class='g-item'><abbr title="{}">
                             <video class="img-fluid g-item" preload='auto' muted onclick="sclick('{}')">
                             <source src="{}{}"/>
                             </video>
                             </abbr></div></div>""".format(str(i[1:-3]).strip('()').replace("'", ''),
                                                     i[0].split('.')[0],
                                                     settings_file.images_path, i[0])
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

    def details(self):
        img_id = self.request['path'].split("/")[-1]
        tags = db.search_by_id(img_id)
        if len(tags) >= 1:
            tags = [x for x in tags[0] if x is not None]
            if tags[0].split('.')[1] != 'webm':
                p = '<img src="/images/{}" class="img img-fluid">'.format(tags[0])
            else:
                p = """<video class="img img-fluid" preload='auto' autoplay controls muted loop>
                                <source src="/{}{}"/>
                                </video>""".format(settings_file.images_path, tags[0])
            data = open('extra/image.html', 'r').read().format(img_id, p, tags[0], tags[0],
                                                               str(["<a href='/?query={}&page=1'>{}</a>".format(f, f)
                                                                    for f in [x for x in tags[1:-3]] if
                                                                    f != "None"]).strip("[]").replace('"', ''))
            self.send_header(200)
            self.send_data(data)
        else:
            self.send_header(404)

    def die(self):
        self.send_header(200)
        self.send_data("Done")
        os._exit(0)

    def dl(self):
        try:
            with open(str(settings_file.images_path + self.request['params']['id']), 'rb') as t:
                temp = t.read()
        except FileNotFoundError:
            self.send_header(404)
        except KeyError:
            self.send_header(404)
        except Exception:
            self.send_header(500)
        else:
            self.send_header(200, self.request['params']['id'].split('.')[-1])
            self.send_data(temp)
            del temp

    def raw_dl(self):
        try:
            with open(str(settings_file.images_path + self.request['params']['id']), 'rb') as j:
                temp = j.read()
        except Exception:
            self.send_data(str(500))
        else:
            self.send_data(temp)
            del temp

    def predictor(self):
        if "mobile" in self.request['user-agent'].lower():
            self.readiness = 1
            del self
        predictor = predict.Predictor()
        try:
            matched = predictor.predict(self.request['params']['phrase'])
            if len(matched) == 0 or len(matched) == 1:
                self.send_header(200)
                self.send_data('')
            else:
                self.send_header(200)
                self.send_data(str(matched))
        except Exception:
            self.send_header(500)

    def serve(self):
        self.log_request()
        if self.request['path'] == '/' and self.request['query'] is None:
            self.index()
        elif self.request['path'].split('/')[1] == 'images' and self.request['path'].split('/')[2] is not '':
            self.show_img()
        elif self.request['path'] == '/export' and self.request['params']['id'] is not None:
            self.exporter()
        elif self.request['path'] == '/' and self.request['query'] is not None:
            self.results()
        elif "/image/" in self.request['path']:
            self.details()
        elif self.request['path'] == '/panic' or self.request['path'] == '/shutdown':
            self.die()
        elif self.request['path'] == '/dl' and 'id' in self.request['params']:
            self.dl()
        elif self.request['path'] == '/raw' and 'id' in self.request['params']:
            self.raw_dl()
        elif self.request['path'] == '/predict' and 'phrase' in self.request['params']:
            self.predictor()
        else:
            try:
                self.request['path'] = self.request['path'].replace('..', '')
                f_type = self.request['path'].split('.')[-1]
                with open(os.curdir + self.request['path'], 'rb') as j:
                    data = j.read()
            except FileNotFoundError:
                self.send_header(404)
            except Exception:
                self.send_header(500)
            else:
                self.send_header(200, f_type)
                self.send_data(data)


def run():
    tc = ThreadController()
    tc.start()
    if settings_file.share_images is True:
        UDPsrv = UDPHandler()
        UDPsrv.start()
    if settings_file.run_follower is True:
        follower = Thread(target=follow.run)
        follower.start()
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((settings_file.web_ip, settings_file.web_port))
    sock.listen(10)
    print("Server started at http://{}:{}".format(settings_file.web_ip, settings_file.web_port))
    while True:
        try:
            conn, addr = sock.accept()
            newT = Handler(conn, addr[0])
            newT.start()
            tc.threads.append(newT)
        except ConnectionResetError:
            pass


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        os._exit(0)
