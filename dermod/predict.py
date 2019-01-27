from dermod import db, input_parser
import settings_file


def gen_list():
    unparsed = db.get_all_entries()
    halfparsed = []
    tags = []
    for i in unparsed:
        halfparsed.append([x for x in i[1:-5] if x != 'None'])
    for i in halfparsed:
        for j in i:
            tags.append(j)
    tags = list(sorted(set(tags)))
    tags_dict = {}
    for i in tags:
        tags_dict[str(i[0])] = []
    for i in tags:
        tags_dict[str(i[0])].append(i)
    return tags_dict


cache = gen_list()


class Predictor:

    def __init__(self):
        self.tags_cache = cache
        self.compiled = ''
        self.matching = []
        self.previous = []
        self.inp = []

    def predict(self, string):
        self.inp, self.previous = input_parser.predictor_parser(string)
        for i in self.tags_cache[self.inp[1][0]]:
            if self.inp[0].startswith('-') is False:
                if self.inp[1] in i[:len(self.inp[1])]:
                    self.matching.append(i)
            else:
                if (self.inp.strip('-') in i[:len(self.inp.strip('-'))]) is True:
                    self.matching.append(i)
        self.matching = list(sorted(set(self.matching)))
        return self.compile_html()

    def compile_html(self):
        for i in self.matching[:settings_file.predict_tags]:
            if len(self.previous) == 0:
                self.compiled += '<option value="{}{}">'.format(self.inp[0], i)
            else:
                self.compiled += '<option value="{}, {}{}">'.format(
                    ",".join(self.previous), self.inp[0], i)
        return self.compiled
