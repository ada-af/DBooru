import settings_file

class Module_Options:

    def __init__(self, data, name):
        self.name = name
        self.options = dict()
        self._disassemble(data)

    def _disassemble(self, data):
        for i in data:
            if i:
                self.options[i.split('=')[0].strip()] = i.split('=')[
                    1].split('#')[0].strip()


class ThumbFile:
    def __init__(self, fname):
        self.name = settings_file.thumbs_path+f"/thumb_{fname}"


class Option:

    def __init__(self, data):
        self.name = ""
        self.description = []
        self.examples = []
        self.require_example = False
        self.format = ""
        self.isblock = False
        self.options = []
        self.value_now = None
        self._disassemble(data)

    def _disassemble(self, data):
        if data[-1] == data[-1].split('=')[0].strip():
            self.isblock = True
            for j in data:
                if j == '':
                    pass
                else:
                    self.name = j.split("# ")[1].strip()
                    break
        else:
            for i in data[:-1]:
                if i.lower().startswith("# example:"):
                    self.examples.append(i[1:].strip())
                elif i.lower().startswith("# format:"):
                    self.format = i.split("=")[1].strip()
                elif i.lower().startswith("# options:"):
                    self.options = i.split(":", maxsplit=1)[1].strip()
                elif i.lower().startswith("# require example"):
                    self.require_example = True
                elif i == '':
                    pass
                else:
                    self.description.append(i[1:].strip())
            self.name = data[-1].split('=')[0].strip()
            self.value_now = data[-1].split('=', maxsplit=1)[1].strip()


class DBImage:
    def __init__(self, data=None):
        if isinstance(data, list) or isinstance(data, tuple):
            self.no_p_fname = data[0]
            self.tags = list(
                sorted(set([x for x in data[1].split(',,') if x != '' and x != ' '])))
            self.width = data[2]
            self.height = data[3]
            self.ratio = data[4]
            self.link = data[5]
            self.prefix = data[6]
            self.id = data[7]
            self.fformat = self.no_p_fname.split('.')[-1]
            self.fname = self.prefix + self.no_p_fname
        else:
            self.no_p_fname
            self.tags
            self.width
            self.height
            self.ratio
            self.link
            self.prefix
            self.id
            self.fformat = self.no_p_fname.split('.')[-1]
            self.fname = self.prefix + self.no_p_fname

    def __repr__(self):
        return f"<Image {self.prefix}{self.id}>"