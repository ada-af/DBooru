import settings_file

class Module_Options:

    def __init__(self, data, name):
        self.name = name
        self.options = dict()
        self._disassemble(data)

    def _disassemble(self, data):
        for i in data:
            if i:
                self.options[i.split('=')[0].strip()] = i.split('=')[1].split('#')[0].strip()

class ThumbFile:
    def __init__(self, fname):
        self.name = f"thumb_{fname}"
        open(settings_file.thumbs_path+self.name, "wb").close()

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