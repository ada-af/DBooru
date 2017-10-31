from settings_file import *
# Модуль, включающий в себя все используемые в данной программе фильтры


def parser(string):
    string = string.replace("%2C", ',').replace("+", " ").replace("%25", "%")
    string = string.lower().split(',')
    half_parsed = []
    for i in string:
        half_parsed.append(i.strip())
    search = []
    remove = []
    for i in half_parsed:
        if i.startswith('-'):
            remove.append(i.replace('-', ''))
        else:
            search.append(i)
    for i in remove:
        if i in search:
            search.remove(i)
    return {"search": search, "remove": remove}


def json_parser(string):
    string = string.replace("'", '"')
    string = string.split('"id":"')[1:]
    ids = []
    form = []
    links = []
    tags = []
    for i in string:
        ids.append(i.split('","')[0])
        k = i.split('original_format')[1]
        k = k.split('":"')[1].split('","')[0]
        form.append(k)
        k = i.split('","large":"')[1]
        k = k.split('","tall"')[0]
        links.append(k)
        tags.append(i.split('"tags":"')[1].split('"')[0])
    return ids, form, links, tags


def json_parser_v2(string):
    string = string.replace("'", '"')
    string = string.split('"id":"')[1:]
    ids = []
    form = []
    links = []
    tags = []
    lst = []
    for i in string:
        ids.append(i.split('","')[0])
        k = i.split('original_format')[1]
        k = k.split('":"')[1].split('","')[0]
        form.append(k)
        k = i.split('","large":"')[1]
        k = k.split('","tall"')[0]
        links.append(k)
        tags.append(i.split('"tags":"')[1].split('","')[0])
    for i in range(len(ids)):
        lst.append(str(ids[i] + ',,,' + form[i] + ',,,' + links[i] + ',,,' + tags[i]))
    return lst


def results_parser(list_tuple):
    results = list_tuple
    res_num = (len(list(results)) / showing_imgs) + 1
    pages = []
    lists = []
    for k in range(0, int(res_num) + 1):
        pages.append(k)
    for i in range(0, len(list(results)), showing_imgs):
        lists.append(list(results)[i:i + showing_imgs])
    pages = dict(zip(pages, lists))
    return pages


def name_tag_parser(fname):
    unparsed = open(fname).read()
    halfparsed = unparsed.split("\n")
    parsed = []
    for i in halfparsed[:-1]:
        parsed.append(i.split(',,,'))
    del unparsed, halfparsed
    return parsed


def web_arg_parser(bytes):
    bytes = bytes.split()[1]
    stroke = bytes.decode()
    stroke = stroke.split("?")[1]
    stroke = stroke.split("&")
    s_query = final = {}
    for i in stroke:
        s_query[i.split("=")[0]] = final[i.split("=")[0]] = i.split("=")[1]
    try:
        s_query = s_query['query'].replace("%2C", ',').replace("+", " ").replace("%25", "%")
        final["query"] = parser(final["query"])
    except Exception:
        pass
    return final, s_query


def web_arg_parser_v2(params):
    params = params\
        .replace("%24", '$')\
        .replace("%2C", ',')\
        .replace("+", " ")\
        .replace("%25", "%")\
        .replace("%2A", "*")\
        .replace("%3A", ":")\
        .replace("%3C", "<")\
        .replace("%3E", ">")\
        .replace("%20", " ")\
        .split("&")
    temp = {}
    for i in params:
        i = i.split('=')
        temp = dict(temp, **{i[0]: i[1]})
    params = temp
    del temp
    params['query'] = params['query'].replace("%3D", "=")
    query = parser(params['query'].repl)
    return params, query


def request_parser(request):
    request = request.decode()
    splitted = request.split("\r\n")
    path = splitted[0].split(" ")[1].split('?')[0]
    try:
        params = splitted[0].split(" ")[1].split('?')[1]
        if "query" in params:
            params, query = web_arg_parser_v2(params)
        else:
            query = None
            p = {}
            for i in params.split("&"):
                p = dict(p, **{i.lower().split('=')[0]: i.lower().split('=')[1]})
            params = p
    except IndexError:
        params, query = (None, None)
    parsed_request = {'method': splitted[0].split(" ")[0], 'path': path, 'params': params, 'query': query}
    for i in splitted[1:-2]:
        i = i.split(':', maxsplit=1)
        tmp = {i[0].lower(): i[1].strip()}
        parsed_request = dict(parsed_request, **tmp)
    return parsed_request
