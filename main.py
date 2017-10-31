#!/bin/python
import os
import webbrowser
import shutil
from settings_file import *
from dermod import db
from dermod import derpilist_v2
from dermod import derpiload_v3 as derpiload_v3
from dermod import input_parser as ip


# Начало функции справки
def show_help(case):
    tags_msg = """\nSearch syntax:
    Tags are not case-sensitive
    Tags must be separated by comma ','
    Example: <ta1, TAg2> ('TAg2' will be the same as 'tag2')
    Excluding tag from search made by adding '-' before tag
    Example: <tag1, -tag3> (In this case tag3 will be excluded from search output)"""
    if str(case) == "1":
        print("<any tags, split, by comma> to search in DB")
        print("<get images> loads every picture you faved/upvoted (may be changed in settings_file.py)")
        print("<total> prints amount of pictures you have in DB")
        print("<count <tag>> prints amount of pictures tagged by <tag>")
        print("<show <filename>> opens image in default image viewer")
        print("<quit> or <exit> to exit")
        print("<help> shows this message again")
        print(tags_msg)
    elif str(case) == '2':
        print("<any tags, split, by comma> to search in DB")
        print("<filter <tag>> to remove pictures that tagged by <tag>")
        print("<add <tag>> to remove pictures that not tagged by <tag>")
        print("<any number bigger than 0> to show search output")
        print("<show <filename>> opens image in default image viewer")
        print("<back> to return to main menu")
        print("<quit> or <exit> to exit")
        print("<help> shows this message again")
        print(tags_msg)
# Конец


def query_cycle(results):
    if len(results) == 0:  # Обработка случая, при котором картинок не было найдено
        print("Nothing found.")
        main_cycle()
    else:
        print("Found {} pages".format(len(results.keys())))
        while True:
            inp = input("\nSearch@DB> ")  # Получение команд пользователя
            inp = inp.lower()
            if inp == "back":
                main_cycle()

            elif inp.isnumeric():  # Обрабатывает номера страниц, и показывает их содержимое
                try:
                    for i in results[(int(inp)-1)]:
                        #i = tuple(filter('None'.__ne__(), i))
                        i = [x for x in i if x != "None"][:-3]
                        print(str(i[0]) + " "*(15 - len(i[0])) + " => " + str(i[1:showing_tags]).strip("()"))
                except KeyError:
                    print('There is no page named {}'.format(inp))

            elif "show" in inp:  # Показ картинки с указанным именем. Использует средства ОС
                inp = inp.split("show")[1]
                try:
                    if os.name != "nt":
                        webbrowser.open(str(images_path + inp.strip()))
                    else:
                        os.system(str("explorer.exe " + images_path + inp.strip()))
                except FileNotFoundError:
                    print("File doesn't exist.")

            elif "export" in inp:  # Копирует картинку с заданным именем в папку указанную в export_path
                for i in results.keys():
                    for k in results[i]:
                        try:
                            shutil.copy(str(images_path + k[0]), str(export_path + k[0]))
                        except FileNotFoundError:
                            os.mkdir(export_path)
                        else:
                            pass

            elif inp == '':  # Обрабатывает пустую строку, во избежание "аварийного закрытия" программы
                pass

            elif inp == "help":  # Показ страницы помощи
                show_help(2)

            elif inp == 'quit' or inp == 'exit':  # Обработка выхода из программы
                os._exit(0)

            elif 'add' in inp:  # Добавляет тэги к уже существуюещму запросу и ищет картинки заного (используется для уточнения поиска)
                inp = inp.strip().split("add ", 1)[1:]
                inp = inp[0].split(",")
                for i in inp:
                    results = db.add_query(results, i)
                query_cycle(results)

            elif 'filter' in inp:  # Добавляет теги, которые убирают картинки из поиска и ищет картинки заного
                inp = inp.strip().split("filter ", 1)[1:]
                inp = inp[0].split(",")
                results = db.filter_query(results, inp)
                query_cycle(results)

            else:  # Остальные случаи расцениваются как теги и с их использованием будет выполнен поиск картинок
                query = ip.parser(inp)
                results = db.search(query['search'], query['remove'])
                query_cycle(results)


# Цикл главного меню
# Обрабатывает команды не связанные с поиском картинок
def main_cycle():
    inp = input("\nDB> ")  # Получение команд пользователя
    inp = inp.lower()
    if inp == "get images":  # Получает картинки и создаёт базу данных, а также добавляет новые картинки, если будет запущена в следующий раз
        derpilist_v2.run()
        db.fill_db()
        derpiload_v3.run(ids_file)
        print("DB configured successfully")
        shutil.rmtree('tmp')
        os.remove(ids_file)
        print("Image index is up-to-date")
    elif inp == "total":  # Показывает общее кол-во картинок в базе данных
        db.total_found()
    elif "count" in inp:  # Показывает кол-во картинок для определенного тэга
        counttag = inp.strip().split("count")[1].strip()
        db.count_tag(counttag)
    elif inp == '':  # Обрабатывает пустую строку, во избежание "аварийного закрытия" программы
        main_cycle()
    elif "show" in inp:  # Показ картинки с указанным именем. Использует средства ОС
        inp = inp.split("show")[1]
        try:
            if os.name != "nt":
                webbrowser.open(str(images_path + inp.strip()))
            else:
                os.system(str("explorer.exe " + images_path + inp.strip()))
        except FileNotFoundError:
            print("File doesn't exist.")
    elif inp == 'quit' or inp == 'exit':  # Обработка выхода из программы
        os._exit(0)
    elif inp == "help":  # Показ страницы помощи
        show_help(1)
    else:  # Остальные случаи расцениваются как теги и с их использованием будет выполнен поиск картинок
        query = ip.parser(inp)
        results = db.search(query['search'], query['remove'])
        query_cycle(results)
    main_cycle()
show_help(1)
try:
    main_cycle()
except KeyboardInterrupt:
    os._exit(0)