#!/bin/python
import os
import webbrowser
import shutil
from settings_file import *
from dermod import db
from dermod import derpilist_v2
from dermod import derpiload_v3 as derpiload_v3
from dermod import input_parser as ip


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
                        
                        i = [x for x in i if x != "None"][:-3]
                        print(str(i[0]) + " "*(15 - len(i[0])) + " => " + str(i[1:showing_tags]).strip("()"))
                except KeyError:
                    print('There is no page named {}'.format(inp))

            elif "show" in inp:  
                inp = inp.split("show")[1]
                inp = db.search_by_id(inp.strip())[0][0]
                try:
                    if os.name != "nt":
                        webbrowser.open(str(images_path + inp.strip()))
                    else:
                        os.system(str("explorer.exe " + images_path + inp.strip()))
                except FileNotFoundError:
                    print("File doesn't exist.")

            elif "export" in inp:  
                for i in results.keys():
                    for k in results[i]:
                        try:
                            shutil.copy(str(images_path + k[0]), str(export_path + k[0]))
                        except FileNotFoundError:
                            os.mkdir(export_path)
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


def main_cycle():
    inp = input("\nDB> ")  
    inp = inp.lower()
    if inp == "get images":  
        derpilist_v2.run()
        db.fill_db()
        derpiload_v3.run(ids_file)
        print("DB configured successfully")
        shutil.rmtree('tmp')
        os.remove(ids_file)
        print("Image index is up-to-date")
    elif inp == "total":  
        db.total_found()
    elif "count" in inp:  
        counttag = inp.strip().split("count")[1].strip()
        db.count_tag(counttag)
    elif inp == '':  
        main_cycle()
    elif "show" in inp:  
        inp = inp.split("show")[1]
        inp = db.search_by_id(inp.strip())[0][0]
        try:
            if os.name != "nt":
                webbrowser.open(str(images_path + inp.strip()))
            else:
                os.system(str("explorer.exe " + images_path + inp.strip()))
        except FileNotFoundError:
            print("File doesn't exist.")
    elif inp == 'quit' or inp == 'exit':  
        os._exit(0)
    elif inp == "help":  
        show_help(1)
    else:  
        query = ip.parser(inp)
        results = db.search(query['search'], query['remove'])
        query_cycle(results)
    main_cycle()
show_help(1)
try:
    main_cycle()
except KeyboardInterrupt:
    os._exit(0)
