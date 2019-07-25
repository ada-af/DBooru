#!/usr/bin/env python3
import imghdr
import json
import math
import os
import subprocess
import sys
import tempfile
from multiprocessing import Process
from threading import Thread

import jinja2
from flask import Flask, jsonify, redirect, render_template, request,\
    send_from_directory, url_for, send_file, Response

import main
import settings_file
from dermod import db
from dermod import input_parser as ip
from dermod import mime_types as mimes
from dermod import predict

try:
    import PIL.Image as Image
except ImportError:
    pass

try:
    os.remove("update.lck")
except Exception:
    pass

DBooru = Flask(__name__)
DBooru.config.from_pyfile("settings_file.py", silent=True)


@DBooru.route('/', methods=["GET"])
def index():
    return render_template('index.html')


@DBooru.route('/search', methods=['GET'])
def search():
    page = request.args.get('page', default=1, type=int)
    query = request.args.get('q', default='', type=str)
    db_search_list = ip.parser(query)
    try:
        results, total = db.search(db_search_list['search'],
         db_search_list['remove'], page=page-1)
    except (IndexError, KeyError):
        pass
    return render_template('results.html', search=query, page=page,
        total_images=total, results=results, settings_file=settings_file, str=str,
        ceil=math.ceil, max=max)


@DBooru.route('/image/<string:img_id>')
def image(img_id):
    prefix, img_id = img_id.split("_")
    image = db.search_by_id(img_id, prefix=prefix)
    page = request.args.get('page', default=1, type=int)
    query = request.args.get('q', default='', type=str)
    return render_template('image.html', image=image)


@DBooru.route("/raw/<string:fname>")
def raw(fname):
    return send_file(settings_file.images_path+fname)

@DBooru.route("/update")
def update():
    if os.path.exists("update.lck") is False:
        open("update.lck", 'w').write('1')
        j = "DB Update started in background."
        stat = 200
        p = Process(main.update_db())
        p.start()
        os.remove('update.lck')
    else:
        j = "Update in process"
        stat = 409
    j = Response(j, status=stat)
    return j

@DBooru.route("/random")
def random():
    img = db.random_img()[0]
    result = str("/image/"+img[-2]+img[0].split('.')[0])
    return redirect(result)

@DBooru.route("/dl/<string:fname>")
def dl(fname):
    return send_file(settings_file.images_path+fname, as_attachment=True)

def encode_PIL(fname, tf):
        img = Image.open(settings_file.images_path+fname)
        img.thumbnail((500, 500), Image.ANTIALIAS)
        if fname.split('.')[-1] == 'gif':
            img.save(tf.name, "GIF")
        else:
            img.save(tf.name, "JPEG")


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
    #subprocess.call(cmd, stdout=open(os.devnull, 'w'))
    os.system(cmd)


@DBooru.route("/thumbnail/<string:fname>")
def thumbnail(fname):
    tf = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
    tf.close()
    if settings_file.thumbnailer.lower() == 'ffmpeg':
        encode_FFMPEG(fname, tf)
    elif settings_file.thumbnailer.lower() == 'pil':
        encode_PIL(fname, tf)
    else:
        os.remove(tf.name)
        tf.name = settings_file.images_path+fname
    return send_file(tf.name)


@DBooru.route("/next/<string:id>")
def next(id):
    f = []
    starting = int(id.split('_')[1])
    x = starting+1
    data = ""
    code = 200
    while True:
        f = db.search_by_id(x)
        if f != []:
            data = str(f[6]+str(f[7]))
            break
        elif abs(starting-x) >= 300:
            code = 404
            break
        else:
            x += 1
    return Response(data, status=code)


@DBooru.route("/previous/<string:id>")
def previous(id):
    f = []
    starting = int(id.split('_')[1])
    x = starting-1
    data = ""
    code = 200
    while True:
        f = db.search_by_id(x)
        if f != []:
            data = str(f[6]+str(f[7]))
            break
        elif abs(starting-x) >= 300:
            code = 404
            break
        else:
            x -= 1
    return Response(data, status=code)


@DBooru.route("/json/search")
def api_search():
    page = request.args.get('page', default=1, type=int)
    query = request.args.get('q', default='', type=str)
    db_search_list = ip.parser(query)
    try:
        results, total = db.search(db_search_list['search'],
         db_search_list['remove'], page=page-1)
    except (IndexError, KeyError):
        pass
    del total
    result = {}
    k = 0
    for _ in results:
        fname = {'filename': _[0]}
        tags = {'tags': _[1].split(",,")[1:-2]}
        height = {'height': _[2]}
        width = {'widht': _[3]}
        ratio = {'ratio': _[4]}
        source_link = {'source_link': _[5]}
        prefix = {'prefix': _[6]}
        thumbnail = {'thumb': "//"+request.host+"/thumbnail/"+prefix['prefix']+fname['filename']}
        full = {'full': "//"+request.host+"/raw/"+prefix['prefix']+fname['filename']}
        __ = dict(fname, **tags, **height, **width,**ratio,**source_link, **prefix, **thumbnail)
        __.update(full)
        result[k] = __
        k += 1
    result = json.dumps(result)
    return Response(result, mimetype="application/json")
    

if __name__ == "__main__":
    DBooru.run(host=settings_file.web_ip, port=settings_file.web_port)
