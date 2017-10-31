import sqlite3
import os
import sys
from dermod import input_parser as ip
from settings_file import *
from datetime import datetime


globals().update()


def precomp():
    global tag_col, tag_col_full, tag_col_serv
    tag_col = 'fname, '
    h = 'tag{}, '
    for i in range(1, 41):
        tag_col += h.format(i)
    tag_col = tag_col[:-2]
    tag_col_full = tag_col + ', height, width, ratio'
    tag_col_serv = 'height, width, ratio'
    #print(tag_col)


def suppress_errs(supp):  # Скрывает ошибки и предупреждения возникающие при работе программы
    if supp is True:
        suppressor = open(os.devnull, 'w')
        sys.stderr = suppressor
    else:
        pass


def errors_init():  # Скрывает ошибки и предупреждения возникающие при работе программы
    suppress_errs(suppressor)


def init_db():  # Инициализирует соединение с базой данных
    global cursor
    global conn
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()


def total_found():  # Обрабатывает запрос общего кол-ва картинок в базе
    init_db()
    print("Images in DataBase =>", cursor.execute("SELECT count(*) FROM {} WHERE {}".format(table_name, columns[0])).fetchone()[0])


def mkdb(table_name):  # Создаёт базу данных по заданным в settings_file.py
    init_db()
    cursor.execute('drop table IF EXISTS {}'.format(table_name))

    sample = """CREATE TABLE {}({})""".format(table_name, tag_col_full)

    cursor.execute(sample)
    conn.commit()


def fill_db():  # Заполняет базу данных данными полученным через API Derpibooru
    print("\nFilling DB")
    global table_name
    global tag_amount
    init_db()
    mkdb(table_name)
    unparsed = open(ids_file).read()
    halfparsed = unparsed.strip("\n").split("\n")
    for i in halfparsed:
        i = i.split(",,,")
        k = i[6].split(",")
        if len(k) < 40:
            k += ["None"] * (40 - len(k))
        elif len(k) == 40:
            pass
        elif len(k) > 40:
            k = k[:40]
        f = [x.strip("'").strip(' ') for x in k]
        k = str(k).strip("[]").replace('" ', '"').replace(' "', '"').replace('\' ', '\'').replace(' \'', '\'')
        j = f"INSERT INTO {table_name} VALUES ('{i[0]}.{i[1]}', {k}, '{i[3]}', '{i[4]}', '{i[5]}')"
        cursor.execute(j)
    cursor.execute(f"delete from {table_name} where rowid not in (select min(rowid) from {table_name} group by fname)")
    conn.commit()


def count_tag(tag_to_count):
    init_db()

    sample = """select count(*) FROM {} where tag1 LIKE '%{}%'""".format(table_name, tag_to_count)
    for i in range(2, tag_amount + 1):
        sample += " OR tag{} LIKE '%{}%'".format(i, tag_to_count)
    output = list(cursor.execute(sample))

    print(str(output[0]).strip("()").replace(",", "") + " images tagged {}".format(tag_to_count))


def search(list_search, list_remove):  # Обработчик поиска по тэгам
    init_db()
    special_fields = []
    for i in list_search:
        if '=' in i or '<' in i or '>' in i:
            special_fields.append(i)
            list_search.remove(i)

    if len(list_search) != 0:
        mkdb('temp1')
        sample = "INSERT INTO temp1 SELECT * FROM {} WHERE '{}' in ({})".format(table_name, list_search[0], tag_col)
        cursor.execute(sample)
        cursor.execute("delete from temp1 where rowid not in (select min(rowid) from temp1 group by fname)")
        results = list(cursor.execute("SELECT * FROM temp1"))
        conn.commit()
    else:
        mkdb('temp1')
        sample = "INSERT INTO temp1 SELECT * FROM {}".format(table_name)
        cursor.execute(sample)
        cursor.execute("delete from temp1 where rowid not in (select min(rowid) from temp1 group by fname)")
        results = list(cursor.execute("SELECT * FROM temp1"))
        conn.commit()

    for i in list_search[1:]:
        mkdb('temp')
        smp = "INSERT INTO temp SELECT * FROM temp1 where '{}' in ({})".format(i, tag_col)
        cursor.execute(smp)
        conn.commit()
        mkdb('temp1')
        cursor.execute("INSERT INTO temp1 SELECT * FROM temp")
        results = list(cursor.execute("select * from temp1"))
        conn.commit()
    results = ip.results_parser(results)

    if len(list_remove) == 0:
        pass
    else:
        for i in list_remove:
            cursor.execute("DELETE FROM temp1 WHERE '{}' in ({})".format(i, tag_col))
            conn.commit()
        results = list(cursor.execute("select * from temp1"))
        results = ip.results_parser(results)
        conn.commit()

    if len(special_fields) == 0:
        return results
    else:
        results = special_f(special_fields)
        results = ip.results_parser(results)
        return results


def special_f(specials):

    def src(value, field, sym):
        mkdb('temp')
        smp = "INSERT INTO temp SELECT * FROM temp1 where cast({} as int) {} {}".format(field, sym, value)
        cursor.execute(smp)
        conn.commit()
        mkdb('temp1')
        cursor.execute("INSERT INTO temp1 SELECT * FROM temp")
        results = list(cursor.execute("select * from temp1"))
        conn.commit()
        return results

    for i in specials:
        i = i.replace("*", '%')
        splitter = ""
        for k in i:
            if k == "=" or k == "<" or k == ">":
                splitter += str(k)
            else:
                pass
        i = i.split(splitter)
        if i[0] == 'height':
            results = src(i[1], i[0], splitter)
            conn.commit()
        elif i[0] == 'width':
            results = src(i[1], i[0], splitter)
            conn.commit()
        elif i[0] == 'ratio' or i[0] == 'aspect_ratio':
            results = src(i[1][:10], 'ratio', splitter)
            conn.commit()
    if len(results) == 0:
        results = []
    return results


def search_by_id(img_id):
    init_db()
    result = list(cursor.execute(f"SELECT * FROM {table_name} WHERE fname like '{img_id}.%'"))

    return result

precomp()