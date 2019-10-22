import settings_file
from dermod.aliases import aliases


def parser(string):
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


def name_tag_parser(fname):
    unparsed = open(fname).read()
    halfparsed = unparsed.split("\n")
    parsed = []
    for i in halfparsed[:-1]:
        parsed.append(i.split(';;;'))
    del unparsed, halfparsed
    return parsed


def predictor_parser(string):
    previous = string.split(',')[:-1]
    string = string.split(',')[-1].strip()
    if string.startswith('-'):
        string.split('-', maxsplit=1)
    else:
        string = ['', string]
    return string, previous