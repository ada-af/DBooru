import os
import sqlite3
import sys
import codecs
import logging

from dermod import input_parser as ip
import settings_file


def precomp():
    global tag_col, tag_col_full, tag_col_serv
    tag_col = 'tags'
    tag_col_full = 'fname, tags, height, width, ratio, source_link, prefix, id'
    tag_col_serv = 'height, width, ratio, source_link, prefix, id'
    init_db()
    t = True
    for i in cursor.execute("select * from sqlite_master").fetchall():
        if settings_file.table_name in i:
            t = False
    if t is True:
        mkdb(settings_file.table_name)


def suppress_errs(supp):
    if supp is True:
        logging.raiseExceptions = False


def errors_init():
    suppress_errs(settings_file.suppressor)


def init_db():
    global cursor
    global conn
    conn = sqlite3.connect(settings_file.db_name)
    cursor = conn.cursor()


def total_found():
    init_db()
    print("Images in DataBase =>", cursor.execute("SELECT count(*) FROM {} WHERE {}".format(
        settings_file.table_name, settings_file.columns[0])).fetchone()[0])


def get_all_entries():
    init_db()
    result = list(cursor.execute(
        "SELECT * from {}".format(settings_file.table_name)))
    return result


def mkdb(table_name):
    init_db()
    cursor.execute('drop table IF EXISTS {}'.format(table_name))

    sample = """CREATE TABLE {}({} INT)""".format(table_name, tag_col_full)

    cursor.execute(sample)
    conn.commit()


def fill_db(file=settings_file.ids_file):
    print("\nFilling DB")
    init_db()
    unparsed = open(file).read()
    halfparsed = unparsed.strip("\n").split("\n")
    cnt = 0
    for i in halfparsed:
        i = i.replace('" ', '"').replace(' "', '"').replace(
            '\' ', '\'').replace(' \'', '\'').replace("'", '').replace("\"", "").replace(r"\xc3\xa9", "e")
        i = i.split(",,,")
        k = i[6]
        k = str(k).strip("[]").replace('" ', '"').replace(
            ' "', '"').replace('\' ', '\'').replace(' \'', '\'')
        j = "INSERT INTO {} VALUES ('{}.{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(
            settings_file.table_name, i[0], i[1], k, i[3], i[4], i[5], i[2], i[7], i[0])
        cursor.execute(j)
        if cnt == 10:
            conn.commit()
            cnt = 0
    conn.commit()
    cursor.execute("delete from {table_name} where rowid not in (select min(rowid) from {table_name} group by fname)".format(
        table_name=settings_file.table_name))
    conn.commit()


def count_tag(tag_to_count):
    init_db()

    sample = """select count(*) FROM {} where tags like '%,,{},,%'""".format(
        settings_file.table_name, tag_to_count)
    output = list(cursor.execute(sample))
    print(str(output[0]).strip("()").replace(",", "") +
          " images tagged {}".format(tag_to_count))


def search(list_search, list_remove, page=0):
    init_db()
    special_fields = []
    for i in list_search:
        if 'ratio' in i or "height" in i or "width" in i:
            if ">" in i or "<" in i or "=" in i:
                special_fields.append(i)
                list_search.remove(i)
    mkdb('temp1')
    if len(list_search) != 0:
        autogen_template = "and {} like '%,,{},,%'"
        autogen_query = "SELECT * from {} where {} like '%,,{},,%'".format(settings_file.table_name, tag_col, list_search[0])
        if len(list_search) > 1:
            for i in list_search[1:]:
                autogen_query = autogen_query + autogen_template.format(tag_col, i)
        query = "INSERT INTO temp1 SELECT DISTINCT * from ({})".format(autogen_query)
        cursor.execute(query)
    else:
        sample = "INSERT INTO temp1 SELECT DISTINCT * FROM {}".format(settings_file.table_name)
        cursor.execute(sample)

    if len(list_remove) == 0:
        pass
    else:
        for i in list_remove:
            cursor.execute(
                "DELETE FROM temp1 WHERE {} like '%,,{},,%'".format(tag_col, i))
            conn.commit()

    results = list(cursor.execute(
        "SELECT * from temp1 order by id DESC limit {imgs_amount} offset {offset}"
        .format(imgs_amount=settings_file.showing_imgs, offset=settings_file.showing_imgs*page)))
    total = cursor.execute("SELECT COUNT(*) FROM temp1").fetchone()
    conn.commit()

    if len(special_fields) == 0:
        pass
    else:
        results, total = special_f(special_fields, page)
    
    return results, total


def special_f(specials, page):

    def src(value, field, sym):
        mkdb('temp')
        smp = "INSERT INTO temp SELECT * FROM temp1 where cast({} as REAL) {} {}".format(
            field, sym, value)
        cursor.execute(smp)
        conn.commit()
        mkdb('temp1')
        cursor.execute("INSERT INTO temp1 SELECT * FROM temp")
        results = list(cursor.execute(
            "select * from temp1 order by CAST(id as INTEGER) DESC limit {imgs_amount} offset {offset}"
            .format(imgs_amount=settings_file.showing_imgs, offset=settings_file.showing_imgs*page)))
        conn.commit()
        total = cursor.execute("SELECT COUNT(*) FROM temp1").fetchone()
        return results, total

    for i in specials:
        i = i.replace("*", '%')
        splitter = ""
        for k in i:
            if k == "=" or k == "<" or k == ">":
                splitter += str(k)
        i = i.split(splitter)
        if i[0] == 'height':
            results, total = src(i[1], i[0], splitter)
            conn.commit()
        elif i[0] == 'width':
            results, total = src(i[1], i[0], splitter)
            conn.commit()
        elif i[0] == 'ratio' or i[0] == 'aspect_ratio':
            evaluated = eval(i[1].replace(":", "/").replace("(", ''))
            results, total = src(evaluated, 'ratio', splitter)
            conn.commit()
    if len(results) == 0:
        results = []
    return results, total


def search_by_id(img_id, prefix="%"):
    init_db()
    sql = "SELECT * FROM {} WHERE id = {} and prefix like '{}_'".format(settings_file.table_name, img_id, prefix)
    result = list(cursor.execute(sql))
    if len(result) != 0:
        return result[0]
    else:
        return []


def random_img():
    init_db()
    result = list(cursor.execute(
        "SELECT * FROM {} ORDER BY RANDOM() LIMIT 1".format(settings_file.table_name)))
    return result


def tagged_random(tag):
    init_db()
    result = list(cursor.execute("SELECT * FROM {} WHERE {tag_col} like '%,,{tag},,%' ORDER BY RANDOM() LIMIT 1"
    .format(settings_file.table_name, tag=tag, tag_col=tag_col)))
    return result

precomp()
