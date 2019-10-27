import os
import sqlite3
import sys
import codecs
import logging

from dermod import input_parser as ip
import settings_file

if settings_file.suppress_errors:
    logging.raiseExceptions = False

def precomp():
    global tag_col, tag_col_full, tag_col_serv
    tag_col = 'tags'
    tag_col_full = 'fname, tags, height, width, ratio, source_link, prefix, id'
    tag_col_serv = 'height, width, ratio, source_link, prefix, id'
    init_db()
    t = [x[1] for x in cursor.execute("select * from sqlite_master").fetchall()]
    if "images" not in t:
        mkdb("images")
            

def init_db():
    global cursor
    global conn
    conn = sqlite3.connect(settings_file.db_name)
    cursor = conn.cursor()


def total_found():
    init_db()
    print("Images in DataBase =>", cursor.execute("SELECT count(*) FROM images where fname").fetchone()[0])


def get_all_entries():
    init_db()
    result = list(cursor.execute(
        "SELECT tags from images"))
    return result


def mkdb(table_name):
    init_db()
    cursor.execute('drop table IF EXISTS {}'.format(table_name))
    sample = """CREATE TABLE {}({} INT)""".format(table_name, tag_col_full)
    cursor.execute(sample)
    conn.commit()

def mk_tdb(table_name):
    init_db()
    cursor.execute('drop table IF EXISTS {}'.format(table_name))
    sample = """CREATE TEMP TABLE {}({} INT)""".format(table_name, tag_col_full)
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
        i = i.split(";;;")
        k = i[6]
        k = str(k).strip("[]").replace('" ', '"').replace(
            ' "', '"').replace('\' ', '\'').replace(' \'', '\'')
        j = "INSERT INTO images VALUES ('{}.{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(
            i[0], i[1], k, i[3], i[4], i[5], i[2], i[7], i[0])
        cursor.execute(j)
        if cnt == 10:
            conn.commit()
            cnt = 0
    conn.commit()
    cursor.execute("delete from images where rowid not in (select min(rowid) from images group by fname)")
    conn.commit()


def count_tag(tag_to_count):
    init_db()

    sample = """select count(*) FROM images where tags like '%,,{},,%'""".format(tag_to_count)
    output = list(cursor.execute(sample))
    print(str(output[0]).strip("()").replace(",", "") +
          " images tagged {}".format(tag_to_count))


def search(list_search, list_remove, page=0):
    init_db()

    # Handle special tags
    specials = []
    spec = []
    for i in list_search:
        if ('ratio' in i or "height" in i or "width" in i) and (">" in i or "<" in i or "=" in i):
            spec.append(i)

    for i in spec:
        list_search.remove(i)
        for j in ['<=', '>=', '==', '=', '>', '<']:
            if len(i.split(j)) == 2:
                sign = j
                splitted = i.strip().split(j)
                splitted[0] = splitted[0].strip()
                splitted[1] = eval(splitted[1].strip().replace(":", "/"))
                specials.append("CAST({} AS REAL){}{}".format(splitted[0], sign, splitted[1]))
                break
    del spec
    if len(specials) > 0:
        specials = " where " + (" and ".join(specials))
    else:
        specials = ""

    mk_tdb('temp1')
   
    if len(list_search) != 0:
        autogen_template = "tags like '%,,{},,%'"
        queries = []

        for i in list_search:
            # or queries generator
            if i.startswith("(") and i.endswith(")"):
                or_list = i.strip("()").split("|")
                or_query = "(" + " or ".join([autogen_template.format(x.strip()) for x in or_list]) + ")"
                queries.append(or_query)
                del or_list, or_query
            # and queries generator
            else:
                queries.append(autogen_template.format(i))
           
        autogen_query = "SELECT * from images where {}".format(" and ".join(queries))
        query = "INSERT INTO temp1 SELECT DISTINCT * from ({})".format(autogen_query)
        cursor.execute(query)
    else:
        sample = "INSERT INTO temp1 SELECT DISTINCT * FROM images"
        cursor.execute(sample)


    if len(list_remove) == 0:
        pass
    else:
        for i in list_remove:
            cursor.execute(
                "DELETE FROM temp1 WHERE {} like '%,,{},,%'".format(tag_col, i))
            conn.commit()

    final_autogen = "SELECT * from temp1 {specials} order by id DESC limit {imgs_amount} offset {offset}".format(
        imgs_amount=settings_file.showing_imgs, offset=settings_file.showing_imgs*page, specials=specials)
    results = list(cursor.execute(final_autogen))

    total = cursor.execute("SELECT COUNT(*) FROM temp1 {}".format(specials)).fetchone()
    conn.commit()

    return results, total


def search_by_id(img_id, prefix="%"):
    init_db()
    sql = "SELECT * FROM images WHERE id = {} and prefix like '{}_'".format(img_id, prefix)
    result = list(cursor.execute(sql))
    if len(result) != 0:
        return result[0]
    else:
        return []


def random_img():
    init_db()
    result = list(cursor.execute(
        "SELECT * FROM images ORDER BY RANDOM() LIMIT 1"))
    return result


def tagged_random(tag):
    init_db()
    search(tag['search'], tag['remove'])
    result = cursor.execute("select * from temp1 order by random() Limit 1").fetchone()

    return result

def get_prev(id):
    init_db()
    result = list(cursor.execute("select * from images where (id<{}) order by id desc limit 1".format(int(id))).fetchall())[0]
    return result

def get_next(id):
    init_db()
    result = list(cursor.execute("select * from images where (id>{}) order by id asc limit 1".format(int(id))).fetchall())[0]
    return result

def tagged_get_prev(id, tag):
    init_db()
    search(tag['search'], tag['remove'])
    result = list(cursor.execute("select * from temp1 where (id<{}) order by id desc limit 1".format(int(id))).fetchall())[0]
    return result

def tagged_get_next(id, tag):
    init_db()
    search(tag['search'], tag['remove'])
    result = list(cursor.execute("select * from temp1 where (id>{}) order by id asc limit 1".format(int(id))).fetchall())[0]
    return result

precomp()
