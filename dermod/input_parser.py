import settings_file
from dermod.aliases import aliases


def parser(string):
    string = string.replace("%2C", ',').replace("+", " ").replace("%25", "%")
    string = string.lower().split(',')
    half_parsed = []
    for i in string:
        i = i.strip()
        if i in aliases.keys():
            i = aliases[i]
        elif i in ["-"+x for x in aliases.keys()]:
            i = "-"+aliases[i.strip("-")]
        half_parsed.append(i)
    search = []
    remove = []
    for i in half_parsed:
        if i.startswith('-'):
            remove.append(i.replace('-', ''))
        else:
            search.append(i)
    search = [x for x in search if x != '']  # remove empty strings
    for i in remove:
        if i in search:
            search.remove(i)
    return {"search": search, "remove": [x for x in remove if x != '']}


def results_parser(list_tuple):
    results = list_tuple
    res_num = (len(list(results)) / settings_file.showing_imgs) + 1
    pages = []
    lists = []
    for k in range(0, int(res_num) + 1):
        pages.append(k)
    for i in range(0, len(list(results)), settings_file.showing_imgs):
        lists.append(list(results)[i:i + settings_file.showing_imgs])
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


def web_arg_parser_v2(params):
    params = params\
        .replace("%24", '$')\
        .replace("%2C", ',')\
        .replace("+", " ")\
        .replace("%25", "%")\
        .replace("%2A", "*")\
        .replace("%5C", "\\")\
        .replace("%3A", ":")\
        .replace("%3C", "<")\
        .replace("%3E", ">")\
        .replace("%20", " ")\
        .replace("%3F", "?")\
        .replace("%2F", "/")\
        .replace("%28", "(")\
        .replace("%29", ")")\
        .split("&")
    temp = {}
    for i in params:
        i = i.replace("%26", "&").split('=')
        temp = dict(temp, **{i[0]: i[1]})
    params = temp
    del temp
    params['query'] = params['query'].replace("%3D", "=")
    query = parser(params['query'])
    return params, query


def request_parser(request):
    request = request.decode()
    splitted = request.split("\r\n")
    post_data = splitted[-1]
    path = splitted[0].split(" ")[1].split('?')[0]
    try:
        params = splitted[0].split(" ")[1].split('?')[1]
        if "query" in params:
            params, query = web_arg_parser_v2(params)
        else:
            query = None
            p = {}
            for i in params.split("&"):
                p = dict(p, **{i.lower().split('=')
                               [0]: i.lower().split('=')[1]})
            params = p
    except IndexError:
        params, query = (None, None)
    parsed_request = {'method': splitted[0].split(
        " ")[0], 'path': path, 'params': params, 'query': query}
    for i in splitted[1:-2]:
        i = i.split(':', maxsplit=1)
        tmp = {i[0].lower(): i[1].strip()}
        parsed_request = dict(parsed_request, **tmp)
    parsed_request['post_data'] = post_data
    return parsed_request


def predictor_parser(string):
    string = string.replace("%24", '$')\
        .replace("%2C", ',')\
        .replace("+", " ")\
        .replace("%25", "%")\
        .replace("%2A", "*")\
        .replace("%3A", ":")\
        .replace("%3C", "<")\
        .replace("%3E", ">")\
        .replace("%20", " ")\
        .replace("%3F", "?")\
        .replace("%5C", "\\")\
        .replace("%2F", "/")\
        .replace("%21", "!")\
        .replace("%26", "&")\
        .replace("%28", "(")\
        .replace("%29", ")")
    previous = string.split(',')[:-1]
    string = string.split(',')[-1].strip()
    if string.startswith('-'):
        string.split('-', maxsplit=1)
    else:
        string = ['', string]
    return string, previous
