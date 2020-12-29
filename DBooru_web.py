#!/usr/bin/env python3
import imghdr
from termcolor import colored
import json
import math
import os
import subprocess
import sys
import socket
import time
import string
import tempfile
import re
import webbrowser
from importlib import reload
from multiprocessing import Process
from threading import Thread

import jinja2
from flask import Flask, jsonify, redirect, render_template, request,\
    send_from_directory, url_for, send_file, Response

import main
import settings_file
from dermod import db, threads
from dermod import input_parser as ip
from dermod import mime_types as mimes
from dermod import predict
from dermod.imgloader import Loader
from dermod.helpers import Option, Module_Options, ThumbFile, DBImage

try:
    import PIL.Image as Image
except ImportError:
    pass

if settings_file.keep_thumbs:
    try:
        os.makedirs(settings_file.thumbs_path)
    except FileExistsError:
        pass

try:
    os.remove("update.lck")
except Exception:
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DBooru = Flask(__name__)
DBooru.config.from_pyfile("settings_file.py", silent=True)

DBooru.logger.disabled = settings_file.suppress_errors


@DBooru.route('/predict', methods=['GET'])
def predict_tag():
    pred = predict.Predictor()
    matched = pred.predict(request.args.get('phrase'))
    return jsonify(matched)


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
        results = [DBImage(x) for x in results]
    except (IndexError, KeyError):
        pass
    return render_template('results.html', search=query, page=page,
                           total_images=total, results=results, settings_file=settings_file, str=str,
                           ceil=math.ceil, max=max)


@DBooru.route('/image/<string:img_id>')
def image(img_id):
    prefix, img_id = img_id.split("_")
    image = db.search_by_id(img_id, prefix=prefix)
    image = DBImage(image)
    query = request.args.get('q')
    if query is None:
        query = ""
    return render_template('image.html', image=image, query=query)


@DBooru.route("/raw/<string:fname>")
def raw(fname):
    return send_file(settings_file.images_path+fname)


@DBooru.route("/update")
def update():
    global THREAD_PORT
    # Socket for thread communication
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if os.path.exists("update.lck") is False:
        sock.sendto(b"UPDT", ('127.0.0.1', THREAD_PORT))
        open("update.lck", 'w').write('1')
        j = "DB Update started in background."
        stat = 200
    else:
        j = "Update in process"
        stat = 409
    j = Response(j, status=stat)
    return j


@DBooru.route("/random")
def random():
    img = db.random_img()[0]
    result = str("/image/"+img[-2]+str(img[-1]))
    return redirect(result)


@DBooru.route("/random/<string:tags>")
def tagged_rand(tags):
    tags_list = ip.parser(tags)
    result = db.tagged_random(tags_list)
    return redirect("/image/"+result[-2]+str(result[-1])+"?q="+tags)


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
    add = "" + settings_file.ffmpeg_args
    if fname.split('.')[-1] == 'gif':
        form = "gif"
        if settings_file.gif_to_webp == True:
            form = "webp"
            add = add + " -loop 0"
    else:
        form = settings_file.conv_format
    cmd = "ffmpeg -i {fname} -vf scale=w=500:h=500:force_original_aspect_ratio=decrease {additions} -y -f {format} {tempname}"\
        .format(fname=settings_file.images_path+fname, format=form, tempname=tf.name, additions=add)
    os.system(cmd)


@DBooru.route("/thumbnail/<string:fname>")
def thumbnail(fname):
    if settings_file.thumbnailer == "ffmpeg" and settings_file.keep_thumbs:
        tf = ThumbFile(fname)
    else:
        tf = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
        tf.close()
    if settings_file.thumbnailer.lower() == 'ffmpeg':
        if os.path.isfile(tf.name) and settings_file.keep_thumbs:
            return send_file(tf.name)
        else:
            encode_FFMPEG(fname, tf)
    elif settings_file.thumbnailer.lower() == 'pil':
        encode_PIL(fname, tf)
    else:
        os.remove(tf.name)
        tf.name = settings_file.images_path+fname
    return send_file(tf.name)


@DBooru.route("/next/<string:id>")
def next(id):
    starting = int(id.split('_')[1])
    query = request.args.get('q')
    if query is None or query == "":
        query = ""
        data = db.get_next(starting)
    else:
        tag_list = ip.parser(query)
        data = db.tagged_get_next(starting, tag_list)
    if not data:
        code = 404
        data = ""
    else:
        code = 200
        data = data[6]+str(data[7])

    return Response(data+"?q={}".format(query), status=code)


@DBooru.route("/previous/<string:id>")
def previous(id):
    starting = int(id.split('_')[1])
    query = request.args.get('q')
    if query is None or query == "":
        query = ""
        data = db.get_prev(starting)
    else:
        tag_list = ip.parser(query)
        data = db.tagged_get_prev(starting, tag_list)
    if not data:
        code = 404
        data = ""
    else:
        code = 200
        data = data[6]+str(data[7])

    return Response(data+"?q={}".format(query), status=code)


@DBooru.route("/settings", methods=["GET"])
def settings():
    modules = list(set([x.split(".py")[0] for x in os.listdir("dermod/sitesupport")]) - set(["__init__", "__pycache__"]))
    modules.sort()
    modules_settings = []
    for i in modules:
        with open(f"dermod/sitesupport/{i}.py", 'r+') as f:
            modules_settings.append(Module_Options(f.read().split("# Do not change values")[0].splitlines(), i))
    with open("settings_file.py") as f:
        contents = f.read()
    contents = contents.split("\n\n")
    contents = [Option(x.split("\n")) for x in contents]
    return render_template("settings.html", c=contents, modules_settings=modules_settings, modules=modules, eval=eval, bool=bool, str=str)


@DBooru.route("/settings/<string:option>", methods=["POST"])
def update_settings(option):
    if option == "modules":
        update = []
        for i in list(set([x.split(".py")[0] for x in os.listdir("dermod/sitesupport")]) - set(["__init__", "__pycache__"])):
            if request.form.get(i) is not None:
                update.append(i)
    else:
        got = request.form.get(f'{option}_new_opt').strip("\"'")
        vartype = request.form.get('opt_type')
        if vartype.lower() == 'bool':
            if got.lower() == 'true':
                update = True
            else:
                update = False
        elif vartype.lower() == 'int':
            update = ""
            for i in got:
                if i in string.digits:
                    update += i
            update = int(update)
        else:
            update = f'"{got}"'
    update_line(option, update)
    return redirect(f"/settings#{option}_form")

@DBooru.route("/settings/<string:module>/<string:option>", methods=["POST"])
def update_mod_settings(module, option):
    got = request.form.get(f'{option}_new_opt').strip("\"'")
    update = f'"{got}"'
    update_line(option, update, f"dermod/sitesupport/{module}.py")
    return redirect(f"/settings#{module}_form")


def update_line(option, update, file="settings_file.py"):
    with open(file, 'r+') as f:
        new = ""
        for i in f.readlines():
            new += re.sub(f"^{option} = .*$", f"{option} = {update}", i, count=1)
        f.seek(0)
        f.truncate(0)
        f.write(new)
        f.flush()


def first_run():
    try:
        webbrowser.open(f"http://127.0.0.1:{settings_file.web_port}/settings")
    except:
        print(colored("Unable to start browser\nSettings page http://127.0.0.1:{settings_file.web_port}/settings", 'red'))
    update_line("first_run", False)


@DBooru.route("/reload/<string:imgid>", methods=["PATCH"])
def image_reload(imgid):
    if request.method != "PATCH":
        return
    image_data = DBImage(db.search_by_id(*reversed(imgid.split("_"))))
    print(f"Reloading {image_data.prefix + image_data.no_p_fname}")
    try:
        os.remove(settings_file.images_path + "/" + image_data.prefix + image_data.no_p_fname)
    except:
        pass
    l = Loader(image_data.link, image_data.prefix + image_data.no_p_fname)
    l.start()
    return Response(status=200)

@DBooru.route("/remove/<string:imgid>", methods=["DELETE"])
def remove_image(imgid):
    image_data = DBImage(db.search_by_id(*reversed(imgid.split("_"))))
    db.remove_entry(image_data.id, image_data.prefix)
    try:
        os.remove(settings_file.images_path + "/" + image_data.prefix + image_data.no_p_fname)
    except:
        pass
    return Response(status=200)

@DBooru.route("/json/search")
def api_search():
    if 'db.lck' in os.listdir():
        return Response('[]', status=423)
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
        thumbnail = {'thumb': "//"+request.host +
                     "/thumbnail/"+prefix['prefix']+fname['filename']}
        full = {'full': "//"+request.host+"/raw/" +
                prefix['prefix']+fname['filename']}
        __ = dict(fname, **tags, **height, **width, **ratio,
                  **source_link, **prefix, **thumbnail)
        __.update(full)
        result[k] = __
        k += 1
    result = json.dumps(result)
    return Response(result, mimetype="application/json")


def start_background_tasks():
    if settings_file.enable_polling:
        mon_thread = threads.Settings_monitor()
        mon_thread.start()
    bg_thread = threads.BgTaskHost()
    bg_thread.start()
    time.sleep(1)
    global THREAD_PORT
    THREAD_PORT = bg_thread.port
    print("Background_host thread running on 127.0.0.1:"+str(THREAD_PORT))


if __name__ == "__main__":
    start_background_tasks()
    if settings_file.first_run:
        first_run()
    DBooru.run(host=settings_file.web_ip,
               port=settings_file.web_port,
               debug=settings_file.debugging)
