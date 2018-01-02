domain = 'https://derpibooru.org'
query = "my:faves"
endpoint = "/search.json?q={}".format(query)
paginator = "page={}"
# Must be regexp
empty_page = '{"search":\[\]'
slp = 0.1 # Defines delay between requests
api_key = ""
params = "&key={}".format(api_key)

class Module:
    def __init__(self):
        self.tags = []
        self.ids = []
        self.img_links = []
        self.format = []
        self.height = []
        self.width = []

    def parse(self, string):
        string = string.split('"id":"')[1:]
        self.ids = []
        self.form = []
        self.links = []
        self.tags = []
        self.height = []
        self.width = []
        for i in string:
            self.ids.append(i.split('","')[0])
            k = i.split('"width":')[1]
            k = k.split(',')[0]
            self.width.append(k)
            k = i.split('"height":')[1]
            k = k.split(',')[0]
            self.height.append(k)
            k = i.split('original_format')[1]
            k = k.split('":"')[1].split('","')[0]
            self.form.append(k)
            k = i.split('","full":"')[1]
            k = k.split('","webm":"')[0]
            k = k.split('"},"is_rendered"')[0].replace("//", "https://")
            self.links.append(k)
            self.tags.append(i.split('"tags":"')[1].split('"')[0])