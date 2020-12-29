import os
from os import remove
import sqlite3
import sys
import codecs
import logging

from dermod import input_parser as ip
import settings_file

try:
    import mysql.connector
except ImportError:
    pass

if settings_file.suppress_errors:
    logging.raiseExceptions = False

def precomp():
    global tag_col, tag_col_full, tag_col_serv, rand_func
    tag_col = 'tags'

    if settings_file.use_mysql:
        tag_col_full = '`fname` VARCHAR(256), `tags` MEDIUMTEXT, `height` INT, `width` INT, `ratio` TEXT, `source_link` MEDIUMTEXT, `prefix` VARCHAR(32), `id` INT'
        tag_col_serv = '`height` INT, `width` INT, `ratio` TEXT, `source_link` MEDIUMTEXT, `prefix` VARCHAR(32), `id` INT'
        rand_func = "RAND()"
    else:
        tag_col_full = 'fname, tags, height, width, ratio, source_link, prefix, id INT'
        tag_col_serv = 'height, width, ratio, source_link, prefix, id INT'
        rand_func = "RANDOM()"
    
    if settings_file.use_mysql:
        try:
            conn = mysql.connector.connect(user=settings_file.mysql_user, password=settings_file.mysql_password, db=settings_file.db_name)
        except:
            conn = mysql.connector.connect(user=settings_file.mysql_user, password=settings_file.mysql_password)
            cur = conn.cursor()
            cur.execute("create schema `{}`".format(settings_file.db_name))
            conn.commit()
            del cur
        conn.close()
        del conn
    conn, cursor = init_db()
    if settings_file.use_mysql:
        cursor.execute("SHOW TABLES")
        t = [x[0] for x in cursor.fetchall()]
    else:
        t = [x[1] for x in cursor.execute("select * from sqlite_master").fetchall()]
    if "images" not in t:
        mkdb("images")
            

def init_db():
    if settings_file.use_mysql:
        conn = mysql.connector.connect(user=settings_file.mysql_user, password=settings_file.mysql_password, db=settings_file.db_name)
    else:
        conn = sqlite3.connect(settings_file.db_name)
    cursor = conn.cursor()
    return conn, cursor


def total_found():
    conn, cursor = init_db()
    cursor.execute("SELECT count(*) FROM images where fname")
    print("Images in DataBase =>", cursor.fetchone()[0])


def get_all_entries():
    conn, cursor = init_db()
    cursor.execute("SELECT tags from images")
    result = list(cursor.fetchall())
    return result


def mkdb(table_name):
    conn, cursor = init_db()
    cursor.execute('drop table IF EXISTS {}'.format(table_name))
    sample = """CREATE TABLE {}({}, PRIMARY KEY (prefix, id))""".format(table_name, tag_col_full)
    cursor.execute(sample)
    conn.commit()
    cursor.execute(f"CREATE UNIQUE INDEX `prefix_id_idx` on {table_name}(id, prefix)")
    conn.commit()

def fill_db(file=settings_file.ids_file):
    print("\nFilling DB")
    conn, cursor = init_db()
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
        j = "REPLACE INTO images VALUES ('{}.{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(
            i[0], i[1], k, i[3], i[4], i[5], i[2], i[7], i[0]).replace('\\', '')
        try:
            cursor.execute(j)
        except:
            j = "INSERT OR REPLACE INTO images VALUES ('{}.{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(
                i[0], i[1], k, i[3], i[4], i[5], i[2], i[7], i[0]).replace('\\', '')
            cursor.execute(j)
        if cnt == 10:
            conn.commit()
            cnt = 0
    conn.commit()
    if not settings_file.use_mysql:
        cursor.execute("delete from images where rowid not in (select min(rowid) from images group by fname)")
        conn.commit()
        conn.execute("VACUUM")
        conn.commit()


def count_tag(tag_to_count):
    conn, cursor = init_db()

    sample = """select count(*) FROM images where tags like '%,,{},,%'""".format(tag_to_count)
    output = list(cursor.execute(sample))
    print(str(output[0]).strip("()").replace(",", "") +
          " images tagged {}".format(tag_to_count))


def search(list_search, list_remove, page=0, return_query=False):
    conn, cursor = init_db()

    # Handle special tags
    specials = []
    spec = []
    for i in list_search:
        if ('ratio' in i or "height" in i or "width" in i) and (">" in i or "<" in i or "=" in i or "!" in i):
            spec.append(i)

    for i in spec:
        list_search.remove(i)
        for j in ['<=', '>=', '<>', '==', "!=", '=', '>', '<']:
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
   
    if len(list_search) != 0:
        autogen_template = "tags like '%,,{},,%'"
        queries = []

        for i in list_search:
            i = i.replace("*", "%")
            # or queries generator
            if i.startswith("(") and i.endswith(")"):
                or_list = i.strip("()").split("|")
                or_query = "(" + " or ".join([autogen_template.format(x.strip()) for x in or_list]) + ")"
                queries.append(or_query)
                del or_list, or_query
            # and queries generator
            else:
                queries.append(autogen_template.format(i))
           
        autogen_query = "SELECT DISTINCT * from images where {}".format(" and ".join(queries))
        #query = "INSERT INTO temp1 SELECT DISTINCT * from ({})".format(autogen_query)
        #cursor.execute(query)
    else:
        autogen_query = "SELECT DISTINCT * FROM images"
        # cursor.execute(sample)


    if len(list_remove) == 0:
        pass
    else:
        remove_queries = []
        for i in list_remove:
            remove_queries.append("{} not like '%,,{},,%'".format(tag_col, i.replace("*", "%")))
        remove_autogen = " and ".join(remove_queries)

        if 'where' in autogen_query:
            autogen_query = autogen_query + " and " + remove_autogen
        else:
            autogen_query = autogen_query + " where " + remove_autogen

    if return_query:
        final_autogen = "{autogen_query} {specials}".format(
            autogen_query=autogen_query, specials=specials)
        return final_autogen
    else:
        final_autogen = "{autogen_query} {specials} order by id DESC limit {imgs_amount} offset {offset}".format(
            autogen_query=autogen_query, imgs_amount=settings_file.showing_imgs, offset=settings_file.showing_imgs*page, specials=specials)
    cursor.execute(final_autogen)
    results = list(cursor.fetchall())

    cursor.execute("SELECT COUNT(*) FROM ({autogen_query}) as T {}".format(specials, autogen_query=autogen_query))
    total = cursor.fetchone()
    conn.commit()

    return results, total
    


def search_by_id(img_id, prefix="%"):
    conn, cursor = init_db()
    sql = "SELECT * FROM images WHERE id = {} and prefix like '{}_'".format(img_id, prefix)
    cursor.execute(sql)
    result = list(cursor.fetchall())
    if len(result) != 0:
        return result[0]
    else:
        return []


def random_img():
    conn, cursor = init_db()
    cursor.execute("SELECT * FROM images ORDER BY {rand} LIMIT 1".format(rand=rand_func))
    result = list(cursor.fetchall())
    return result


def tagged_random(tag):
    conn, cursor = init_db()
    query = search(tag['search'], tag['remove'], return_query=True)
    cursor.execute("select * from ({}) as T order by {rand} Limit 1".format(query, rand=rand_func))
    result = cursor.fetchone()
    return result

def get_prev(id):
    conn, cursor = init_db()
    cursor.execute("select * from images where (id<{}) order by id desc limit 1".format(int(id)))
    result = list(cursor.fetchall())[0]
    return result

def get_next(id):
    conn, cursor = init_db()
    cursor.execute("select * from images where (id>{}) order by id asc limit 1".format(int(id)))
    result = list(cursor.fetchall())[0]
    return result

def tagged_get_prev(id, tag):
    conn, cursor = init_db()
    query = search(tag['search'], tag['remove'], return_query=True)
    cursor.execute("select * from ({}) as T where (id<{}) order by id desc limit 1".format(query, int(id)))
    result = list(cursor.fetchall())[0]
    return result

def tagged_get_next(id, tag):
    conn, cursor = init_db()
    query = search(tag['search'], tag['remove'], return_query=True)
    cursor.execute("select * from ({}) as T where (id>{}) order by id asc limit 1".format(query, int(id)))
    result = list(cursor.fetchall())[0]
    return result

def remove_entry(imgid, prefix):
    conn, cursor = init_db()
    sql = f"delete from images where (id = {int(imgid)}) and (prefix = '{prefix}')"
    print(sql)
    cursor.execute(sql)
    conn.commit()
    conn.close()

precomp()
