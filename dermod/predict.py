from dermod import db, input_parser
import settings_file


def gen_list():
    unparsed = [x[0].split(",,") for x in db.get_all_entries()]
    parsed = set([x for p in unparsed for x in p])
    del unparsed
    return parsed
    


cache = gen_list()


class Predictor():
    def __init__(self):
        self.tags_cache = cache
        self.matched = []
        self.remove = False

    def predict(self, tag):
        if tag.startswith("-"):
            tag = tag[1:]
            self.remove = True
        for i in self.tags_cache:
            if i.startswith(tag.lower()) or i == tag.lower():
                if len(self.matched) > settings_file.predict_tags:
                    break
                else:
                    if self.remove is True:
                        self.matched.append("-"+i)
                    else:
                        self.matched.append(i)
        return self.matched
