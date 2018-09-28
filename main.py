#!/usr/bin/env python3
import os
import sys
import shutil
import webbrowser
import importlib

from dermod import input_parser as ip
from dermod import db, follow, listloader, imgloader
import settings_file


def show_help(case):
    tags_msg = """\nSearch syntax:
    Tags are not case-sensitive
    Tags must be separated by comma ','
    Example: <ta1, TAg2> ('TAg2' will be the same as 'tag2')
    Excluding tag from search made by adding '-' before tag
    Example: <tag1, -tag3> (In this case tag3 will be excluded from search output)
    Special tags: height, width, ratio
    Use Special tags to filter images by size
    Example: height>=100 (Will find images with height of 100 and more)"""
    if str(case) == "1":
        print("<any tags, split, by comma> to search in DB")
        print("<get images> loads every picture you faved/upvoted (may be changed in settings_file.py)")
        print("<get images -f> loads every picture you faved/upvoted Downloads images without checking file existance")
        print("<get images --force> same as <get images -f>")
        print("<get images --fast> checks for new images and downloads them using follower")
        print("<total> prints amount of pictures you have in DB")
        print("<count <tag>> prints amount of pictures tagged by <tag>")
        print("<show <id>> opens image in default image viewer")
        print("<quit> or <exit> to exit")
        print("<help> shows this message again")
        print(tags_msg)
    elif str(case) == '2':
        print("<any tags, split, by comma> to search in DB")
        print("<any number bigger than 0> to show search output")
        print("<show <id>> opens image in default image viewer")
        print("<back> to return to main menu")
        print("<quit> or <exit> to exit")
        print("<help> shows this message again")
        print(tags_msg)


def query_cycle(results):
    if len(results) == 0:
        print("Nothing found.")
        main_cycle()
    else:
        print("Found {} pages".format(len(results.keys())))
        while True:
            inp = input("\nSearch@DB> ")
            inp = inp.lower()
            if inp == "back":
                main_cycle()

            elif inp.isnumeric():
                try:
                    for i in results[(int(inp)-1)]:
                        i = [x for x in i if x != "None"][:-5]
                        tmp = db.search_by_id(str(i[0]).split(".")[0])
                        print(str(tmp[0][-1]+i[0]) + " "*(15 - len(i[0])) +
                              " => " + str(i[1:settings_file.showing_tags]).strip("()"))
                except KeyError:
                    print('There is no page named {}'.format(inp))

            elif "show" in inp:
                inp = inp.split("show")[1]
                try:
                    if os.name != "nt":
                        webbrowser.open(os.path.dirname(os.path.realpath(
                            __file__)) + "/" + str(settings_file.images_path + inp.strip()))
                    else:
                        os.system(str("explorer.exe " + os.path.dirname(
                            os.path.realpath(__file__)) + settings_file.images_path + inp.strip()))
                except FileNotFoundError:
                    print("File doesn't exist.")

            elif "export" in inp:
                try:
                    shutil.copy(os.path.dirname(os.path.realpath(__file__)) + str(settings_file.images_path +
                                                                                  inp.split(" ")[1]),
                                os.path.dirname(os.path.realpath(__file__)) + str(settings_file.export_path +
                                                                                  inp.split(" ")[1]))
                except FileNotFoundError:
                    os.mkdir(settings_file.export_path)
                else:
                    pass

            elif inp == '':
                pass

            elif inp == "help":
                show_help(2)

            elif inp == 'quit' or inp == 'exit':
                os._exit(0)

            else:
                query = ip.parser(inp)
                results = db.search(query['search'], query['remove'])
                query_cycle(results)


def update_db(endwith="\r"):
    for i in settings_file.modules:
        module = importlib.import_module('dermod.sitesupport.{}'.format(i))
        print("\nChecking updates for "+module.__name__.split('.')[-1])
        listloader.run(module=module, endwith=endwith)
        imgloader.run(settings_file.ids_file, endwith=endwith)
        db.fill_db()
        print("DB configured successfully")
        shutil.rmtree('tmp')
        os.remove(settings_file.ids_file)
        print("Image index is up-to-date\n")


def main_cycle():
    inp = input("\nDB> ")
    inp = inp.lower()
    if inp == "get images":
        update_db()
    elif inp == "get images --force" or inp == "get images -f":
        update_db()
    elif inp == "get images --fast":
        follow.run(run_once=True)
    elif inp == "total":
        db.total_found()
    elif "count" in inp:
        counttag = inp.strip().split("count")[1].strip()
        db.count_tag(counttag)
    elif inp == '':
        main_cycle()
    elif "show" in inp:
        inp = inp.split("show")[1]
        try:
            if os.name != "nt":
                webbrowser.open(os.path.dirname(os.path.realpath(
                    __file__))+ "/" + str(settings_file.images_path + inp.strip()))
            else:
                os.system(str("explorer.exe " + os.path.dirname(os.path.realpath(__file__)
                                                                ) + settings_file.images_path + inp.strip()))
        except FileNotFoundError:
            print("File doesn't exist.")
    elif inp == 'quit' or inp == 'exit':
        os._exit(0)
    elif inp == "help":
        show_help(1)
    elif "export" in inp:
        try:
            shutil.copy(os.path.dirname(os.path.realpath(__file__)) + str(settings_file.images_path +
                                                                          inp.split(" ")[1]),
                        os.path.dirname(os.path.realpath(__file__)) + str(settings_file.export_path +
                                                                          inp.split(" ")[1]))
        except FileNotFoundError:
            os.mkdir(settings_file.export_path)
        else:
            pass
    else:
        query = ip.parser(inp)
        results = db.search(query['search'], query['remove'])
        query_cycle(results)
    main_cycle()


try:
    try:
        if sys.argv[1] == "update":
            update_db(endwith="\n")
            os._exit(0)
    except IndexError:
        pass
    main_cycle()
except KeyboardInterrupt:
    os._exit(0)
