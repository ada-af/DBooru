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


def query_cycle(total, query):
    if total == 0:
        print("Nothing found.")
        main_cycle()
    else:
        pages = int(total / settings_file.showing_imgs)+1
        print("Found {} pages".format(pages))
        while True:
            inp = input("\nSearch@DB> ")
            inp = inp.lower()
            if inp == "back":
                break

            elif inp.isnumeric():
                if int(inp) > pages:
                    print("No such page")
                l_s = ip.parser(query)['search']
                l_r = ip.parser(query)['remove']
                results, total = db.search(l_s, l_r, int(inp)-1)
                page_dict = {}
                for i in range(len(results)):
                    page_dict[i+1] = results[i]
                for i in page_dict:
                    print("({}) => {}".format(i, page_dict[i][1].split(",,")[:settings_file.showing_tags]))

            elif "show" in inp:
                inp = inp.split("show")[1]
                try:
                    file_name = str(page_dict[int(inp.strip())][6]) + str(page_dict[int(inp.strip())][0])
                except IndexError:
                    print("Usage: show <id>")
                try:
                    webbrowser.open(os.path.dirname(os.path.realpath(
                        __file__)) + "/" + str(settings_file.images_path.replace('.','') + file_name))
                except FileNotFoundError:
                    print("File doesn't exist.")

            elif "export" in inp:
                inp = inp.split("export")[1]
                file_name = str(page_dict[int(inp.strip())][6]) + str(page_dict[int(inp.strip())][0])
                try:
                    shutil.copy(os.path.dirname(os.path.realpath(__file__)) + str(settings_file.images_path +
                                                                                  file_name),
                                os.path.dirname(os.path.realpath(__file__)) + str(settings_file.export_path +
                                                                                  file_name))
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
                results, total = db.search(query['search'], query['remove'])
                query_cycle(total[0], inp)


def update_db(endwith="\r"):
    for i in settings_file.modules:
        module = importlib.import_module('dermod.sitesupport.{}'.format(i))
        print("\nChecking updates for "+module.__name__.split('.')[-1])
        listloader.run(module=module, endwith=endwith)
        imgloader.run(module, settings_file.ids_file, endwith=endwith)
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
    elif inp == "get images --force":
        update_db()
    elif inp == "get images --fast" or inp == "get images -f":
        follow.run(run_once=True)
    elif inp == "total":
        db.total_found()
    elif "count" in inp:
        counttag = inp.strip().split("count")[1].strip()
        db.count_tag(counttag)
    elif inp == '':
        main_cycle()
    elif inp == 'quit' or inp == 'exit':
        os._exit(0)
    elif inp == "help":
        show_help(1)
    else:
        query = ip.parser(inp)
        results, total = db.search(query['search'], query['remove'])
        query_cycle(total[0], inp)
    main_cycle()


try:
    try:
        if sys.argv[1] == "update":
            update_db(endwith="\r")
            os._exit(0)
    except IndexError:
        pass
    main_cycle()
except KeyboardInterrupt:
    os._exit(0)
