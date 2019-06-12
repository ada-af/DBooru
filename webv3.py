#!/usr/bin/env python3
import json
import math
import os
import socket
import sys
import imghdr
import tempfile
import time
from datetime import datetime
from threading import Thread
from multiprocessing import Process

import settings_file
import main
from dermod import db, follow
from dermod import input_parser as ip
from dermod import mime_types as mimes
from dermod import predict

try:
    import PIL.Image as Image
except ImportError:
    pass

try:
    os.remove("update.lck")``
except Exception:
    pass

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
                self.log_debug("Running threads {} ({} threads destroyed)".format(
                    len(self.threads), p))


class Handler(Thread):

    @staticmethod
    def log_debug(*args):
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        for i in args:
            print("[DEBUG] @ [{}] ".format(t) + str(i))

    def __init__(self, csock, ip, request_debug=False):
        Thread.__init__(self)
        self.conn = csock
        self.req = csock.recv(1024)
        self.ip = ip
        self.request = None
        self.readiness = 0
        self.request_debug = request_debug

    def run(self):
        try:
            self.request = ip.request_parser(self.req)
            if self.request_debug is True:
                self.log_debug(self.request, "\n\n")
            self.serve()
        except Exception as e:
            print(e)
        self.readiness = 1
        quit(0)

    def send_data(self, data):
        try:
            self.conn.send(data.encode())
        except AttributeError:
            self.conn.send(data)

    def close_connection(self):
        self.conn.close()

    def get_len(self, fileobject):
        if fileobject is None:
            return 0
        elif type(fileobject) is str or type(fileobject) is bytes:
            ln = len(fileobject)
        elif type(fileobject) is int:
            ln = fileobject
        else:
            ln = str(fileobject.seek(0, 2))
            fileobject.seek(0)
        return ln

    def send_header(self, code, mime='html', fileobject=None, cache="no-cache"):
        content_len = self.get_len(fileobject)
        mime = mimes.types[mime]
        if code == 200:
            self.conn.sendall(
                """HTTP/1.1 200 OK\nServer: PyWeb/3.0\nCache-Control: {}\nContent-Type: {}\nContent-Length: {}\nX-HTTP-Pony: I'm working hard for you\n\n""".format(cache, mime, content_len).encode())
        elif code == 404:
            self.conn.sendall(
                """HTTP/1.1 404 Not Found\nServer: PyWeb/3.0\nContent-Type: {}\nX-HTTP-Pony: Looks like i'm pretty awful in searching things\n\n""".format(mime).encode())
            self.send_data(
                "<html><body>404 Not Found</body></html>".encode())
            self.close_connection()
        elif code == 500:
            self.conn.sendall(
                """HTTP/1.1 500 Internal Server Error\nServer: PyWeb/3.0\nContent-Type: {}\nX-HTTP-Pony: Well shit...\n\n""".format(mime).encode())
            self.send_data("500 Internal Server Error")
            self.conn.close()
        else:
            self.conn.sendall(
                """HTTP/1.1 {}\nServer: PyWeb/3.0\nContent-Type: {}\nX-HTTP-Pony: Well shit...\n\n""".format(code, mime).encode())
            self.send_data("HTTP Error code {}".format(code))
            self.conn.close()

    def log_request(self):
        request = self.request
        t = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        print("""[REQUEST] [{} @ {}] Made request: {} {} with params {{'params: {}', 'query: {}', 'post_data': {}}}"""
              .format(self.ip, t, request['method'], request['path'], request['params'], request['query'], request['post_data']))

    def index(self):
        with open("extra/index.html", 'rb') as j:
            self.send_header(200, fileobject=j, cache="private, max-age=86400")
            while True:
                i = j.read(1024)
                self.send_data(i)
                if not i:
                    break
        self.close_connection()

    def api_search(self, page=0):
        try:
            results = db.search(
                self.request["query"]['search'],
                self.request["query"]['remove'], page)
            p = results[int(page)]
            true_results = {}
            k = 0
            for _ in p:
                fname = {'filename': _[0]}
                tags = {'tags': _[1].split(",,")[1:]}
                height = {'height': _[2]}
                width = {'widht': _[3]}
                ratio = {'ratio': _[4]}
                source_link = {'source_link': _[5]}
                prefix = {'prefix': _[6]}
                thumbnail = {'thumb': "//"+self.request['host']+"/thumb/"+prefix['prefix']+fname['filename']}
                full = {'full': "//"+self.request['host']+"/raw/"+prefix['prefix']+fname['filename']}
                __ = dict(fname, **tags, **height, **width,**ratio,**source_link, **prefix, **thumbnail)
                __.update(full)
                true_results[k] = __
                k += 1
            p = json.dumps(true_results)
        except (IndexError, KeyError) as e:
            self.send_header(404)
        except Exception as e:
            self.send_header(500)
        else:
            self.send_header(200, fileobject=len(p), mime="json")
            self.send_data(p)
        self.close_connection()

    def show_img(self):
        try:
            f_type = self.request['path'].split('.')[-1]
            with open("{}".format(settings_file.images_path + self.request['path'].split('/')[-1]), 'rb') as j:
                self.send_header(200, f_type, j)
                while True:
                    i = j.read(1024)
                    self.send_data(i)
                    if not i:
                        break
        except FileNotFoundError:
            self.send_header(404)
        self.close_connection()

    def exporter(self):
        try:
            src_file = open(str(settings_file.images_path +
                                self.request['params']['id']), 'rb').read()
        except FileNotFoundError:
            self.send_header(404)
        else:
            try:
                open(str(settings_file.export_path +
                         self.request['params']['id']), 'wb').write(src_file)
            except FileNotFoundError:
                os.mkdir(settings_file.export_path)
                open(str(settings_file.export_path +
                         self.request['params']['id']), 'wb').write(src_file)
            except Exception:
                self.send_header(500)
            else:
                self.send_header(200, fileobject=4)
                self.send_data('Done')
        self.close_connection()

    def results(self):
        try:
            results, total = db.search(
                self.request["query"]['search'], self.request["query"]['remove'],
                     page=int(self.request['params']['page'])-1)
            paginator = self.gen_paginator(total[0])
        except (IndexError, KeyError):
            self.send_header(404)
        except Exception:
            self.send_header(500)
        else:
            pictures = []
            for i in results:
                pictures.append(i)
            p = ''
            for i in list(pictures):
                if i[0].split('.')[1] != 'webm':
                    try:
                        p += """<div class="cont"><div class='g-item'><abbr title="{}"><img src="
                    /thumb/{}" onclick="sclick('{}')" class="img-fluid g-item"></abbr></div></div>""" \
                            .format(str(i[1].split(",,")).replace("'", '').strip("[]")[2:], i[-2]+i[0], i[-2]+i[0].split('.')[0])
                    except Exception:
                        self.send_header(500)
                elif i[0].split('.')[1] == 'webm':
                    p += """<div class="cont"><div class='g-item'><abbr title="{}">
                             <video class="img-fluid g-item" preload='auto' muted onclick="sclick('{}')">
                             <source src="{}{}"/>
                             </video>
                             </abbr></div></div>""".format(str(i[1].split(",,")).replace("'", '').strip("[]")[2:],
                                                           i[-2] +
                                                           i[0].split('.')[0],
                                                           settings_file.images_path, i[-2]+i[0])
            try:
                p = open("extra/results.html", 'r').read().format(self.request['params']['query'],
                                                                  p,
                                                                  paginator)
            except Exception:
                self.send_header(500)
            else:
                self.send_header(200, fileobject=len(p))
                self.send_data(p)
        self.close_connection()

    def details(self):
        img_id = self.request['path'].split("/")[-1].split("_")
        tags = list(db.search_by_id(img_id[1], img_id[0]))
        if len(tags) >= 1:
            tags[1] = tags[1].split(",,")
            if tags[0].split('.')[1] != 'webm':
                p = '<img src="/images/{}" class="ft" id="image" onclick="sw()">'.format(
                    tags[-2]+tags[0])
            else:
                p = """<video class="img img-fluid" preload='auto' autoplay controls muted loop>
                                <source src="/{}{}"/>
                                </video>""".format(settings_file.images_path, tags[-2]+tags[0])
            data = open('extra/image.html', 'r').read().format(img_id[1], p, tags[-2]+tags[0], tags[-2]+tags[0], tags[-2]+tags[0], tags[-3], tags[-3],
                                                               str(['<a href="/?query={}&page=1">{}</a>'.format(f, f)
                                                                    for f in [x for x in tags[1][1:]]]).strip("[]").replace("'", ''))
            self.send_header(200, fileobject=len(data))
            self.send_data(data)
        else:
            self.send_header(404)
        self.close_connection()

    def dl(self):
        try:
            with open(str(settings_file.images_path + self.request['params']['id']), 'rb') as t:
                self.send_header(
                    200, self.request['params']['id'].split('.')[-1], fileobject=t)
                for i in t:
                    self.send_data(i)
        except FileNotFoundError:
            self.send_header(404)
        except KeyError:
            self.send_header(404)
        except Exception:
            self.send_header(500)
        self.close_connection()

    def raw_dl(self):
        try:
            with open(str(settings_file.images_path + self.request['params']['id']), 'rb') as j:
                self.send_header(
                    200, self.request['params']['id'].split('.')[-1], fileobject=j)
                while True:
                    i = j.read(1024)
                    self.send_data(i)
                    if not i:
                        break
        except Exception:
            self.send_data(str(500))

    def predictor(self):
        if settings_file.disable_mobile is True:
            if "mobile" in self.request['user-agent'].lower():
                self.readiness = 1
                del self
        predictor = predict.Predictor()
        try:
            matched = predictor.predict(self.request['params']['phrase'])
            if len(matched) == 0 or len(matched) == 1:
                self.send_header(200, fileobject=0)
                self.send_data('')
            else:
                self.send_header(200, fileobject=str(matched))
                self.send_data(str(matched))
        except Exception:
            self.send_header(500)
        self.close_connection()

    def previous(self):
        f = []
        this = self.request['post_data']
        starting = int(self.request['post_data'].split('_')[1])
        x = starting-1
        while True:
            f = db.search_by_id(x)
            if f != []:
                data = (f[6]+str(f[7]))
                self.send_header(200, fileobject=data)
                self.send_data(data)
                break
            elif (starting-x) >= 300:
                self.send_header(404)
                break
            else:
                x -= 1
        self.close_connection()

    def next(self):
        f = []
        this = self.request['post_data']
        starting = int(self.request['post_data'].split('_')[1])
        x = starting+1
        while True:
            f = db.search_by_id(x)
            if f != []:
                data = (f[6]+str(f[7]))
                self.send_header(200, fileobject=data)
                self.send_data(data)
                break
            elif (starting-x) <= 300:
                self.send_header(404)
                break
            else:
                x += 1
        self.close_connection()

    def gen_paginator(self, total):
        ex = """<li class="page-item{}"><a class="page-link" href="/?query={}&page={}">{}</a></li>"""
        query = self.request['params']['query'].replace("=", "%3D")
        p = "" + ex.format('', query, '1', 'First')
        list_of_pages = range(0, math.ceil(total/settings_file.showing_imgs))
        cur_pg = int(self.request['params']['page'])

        if int(self.request['params']['page']) >= 4:
            for i in list_of_pages[cur_pg-3:cur_pg+4]:
                if int(i)+1 == cur_pg:
                    p += ex.format(" disabled", query, i+1, i+1)
                else:
                    p += ex.format("", query, i+1, i+1)
        elif int(self.request['params']['page']) < 4:
            for i in list_of_pages[0:cur_pg+4]:
                if int(i)+1 == cur_pg:
                    p += ex.format(" disabled", query, i+1, i+1)
                else:
                    p += ex.format("", query, i+1, i+1)
        p += ex.format('', query, math.ceil(total/settings_file.showing_imgs), 'Last')
        return p

    @staticmethod
    def encode_PIL(fname, tf):
        img = Image.open(settings_file.images_path+fname)
        img.thumbnail((500,500), Image.ANTIALIAS)
        if fname.split('.')[-1] == 'gif':
            img.save(tf.name, "GIF")
        else:
            img.save(tf.name, "JPEG")

    @staticmethod
    def encode_FFMPEG(fname, tf):
        add = ""
        if fname.split('.')[-1] == 'gif':
            form = "gif"
            if settings_file.gif_to_webp == True:
                form = "webp"
                add = "-loop 0"
        else:
            form = settings_file.conv_format
        cmd = "ffmpeg -i {fname} -vf scale=w=500:h=500:force_original_aspect_ratio=decrease {additions} -y -f {format} {tempname}"\
            .format(fname=settings_file.images_path+fname, format=form, tempname=tf.name, additions=add)
        os.system(cmd)                

    def thumb(self):
        fname = self.request['path'].split("/")[-1]
        tf = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
        tf.close()
        if settings_file.thumbnailer.lower() == "ffmpeg":
            self.encode_FFMPEG(fname, tf)
        elif settings_file.thumbnailer.lower() == "pil":
            self.encode_PIL(fname, tf)
        else:
            os.remove(tf.name)
            tf.name = settings_file.images_path+fname
        with open(tf.name, 'rb') as nm:
            if fname.split('.')[-1] == 'gif' and settings_file.gif_to_webp is True:
                self.send_header(200, mime="webp", fileobject=nm.seek(0, 2), cache="private, max-age=86400")
            elif fname.split('.')[-1] == 'gif':
                self.send_header(200, mime="gif", fileobject=nm.seek(0, 2), cache="private, max-age=86400")
            else:
                mime = imghdr.what(tf.name)
                if mime is None:
                    mime = "other"
                self.send_header(200, mime=mime, fileobject=nm.seek(0, 2), cache="private, max-age=86400")
            nm.seek(0)
            while True:
                i = nm.read(1024)
                self.send_data(i)
                if not i:
                    break
        nm.close()
        if settings_file.thumbnailer.lower() != "disabled":
            os.remove(tf.name)
        else:
            pass
        self.close_connection()

    def random_image(self):
        img = db.random_img()[0]
        result = str("/image/"+img[-2]+img[0].split('.')[0])
        self.send_header(200, fileobject=result)
        self.send_data(result)
        self.close_connection()

    def tagged_random_image(self):
        img = db.tagged_random(self.request['params']['query'])[0]
        result = str("/image/"+img[-2]+img[0])
        self.send_header(200, fileobject=result)
        self.send_data(result)
        self.close_connection()

    def run_update(self):
        if os.path.exists("update.lck") is False:
            open("update.lck", 'w').write('1')
            j = "DB Update started in background."
            self.log_debug(j)
            self.send_header(200, fileobject=j)
            self.send_data(j)
            self.close_connection()
            p = Process(main.update_db())
            p.start()
            os.remove('update.lck')
        else:
            j = "Update in process"
            self.send_header(409, fileobject=j)
            self.send_data(j)
            self.close_connection()


    def serve(self):
        self.log_request()
        if self.request['path'] == '/' and self.request['query'] is None:
            self.index()
        elif self.request['path'] == '/api/search' and self.request['query'] is not None:
            if 'page' in self.request['params']:
                self.api_search(page=self.request['params']['page'])
            else:
                self.api_search()
        elif self.request['path'] == '/random' and self.request['query'] is not None:
            self.tagged_random_image()
        elif self.request['path'] == '/random':
            self.random_image()
        elif self.request['path'] == '/next' and self.request['method'].upper() == 'POST' and self.request['post_data'] != '':
            self.next()
        elif self.request['path'] == '/previous' and self.request['method'].upper() == 'POST' and self.request['post_data'] != '':
            self.previous()
        elif self.request['path'].split('/')[1] == 'images' and self.request['path'].split('/')[2] is not '':
            self.show_img()
        elif self.request['path'] == '/export' and self.request['params']['id'] is not None:
            self.exporter()
        elif self.request['path'] == '/' and self.request['query'] is not None:
            self.results()
        elif "/thumb/" in self.request['path']:
            self.thumb()
        elif "/image/" in self.request['path']:
            self.details()
        elif self.request['path'] == '/dl' and 'id' in self.request['params']:
            self.dl()
        elif self.request['path'] == '/raw' and 'id' in self.request['params']:
            self.raw_dl()
        elif self.request['path'] == '/predict' and 'phrase' in self.request['params']:
            self.predictor()
        elif self.request['path'] == '/update':
            self.run_update()
        else:
            try:
                self.request['path'] = self.request['path'].replace('..', '')
                f_type = self.request['path'].split('.')[-1]
                with open(os.curdir + self.request['path'], 'rb') as j:
                    self.send_header(200, f_type, fileobject=j, cache="private, max-age=86400")
                    for i in j:
                        self.send_data(i)
            except FileNotFoundError:
                self.send_header(404)
            except Exception:
                self.send_header(500)
            self.close_connection()


def run(request_debug=False):
    tc = ThreadController()
    tc.start()
    if settings_file.run_follower is True:
        follower = Thread(target=follow.run)
        follower.start()
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((settings_file.web_ip, settings_file.web_port))
    sock.listen(64)
    print("Server started at http://{}:{}".format(settings_file.web_ip,
                                                  settings_file.web_port))
    while True:
        try:
            conn, addr = sock.accept()
            newT = Handler(conn, addr[0], request_debug=request_debug)
            newT.start()
            tc.threads.append(newT)
        except ConnectionResetError:
            pass


if __name__ == "__main__":
    try:
        try:
            if sys.argv[1] == "debug":
                run(request_debug=True)
            else:
                run()
        except IndexError:
            run()
    except KeyboardInterrupt:
        os._exit(0)
