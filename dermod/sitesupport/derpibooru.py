query = "my:faves" # "my:upvotes"
api_key = "API-KEY GOES HERE"

# Do not change values below line 4

domain = 'https://derpibooru.org'
endpoint = "/search.json?q={}".format(query)
paginator = "&page={}"
# Must be regexp
empty_page = '\{"search":\[\],"'
slp = 0.2 # Defines delay between requests
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
        string = string.split('interactions":[{"')[0]
        string = string.split('"id":')[1:]
        self.ids = []
        self.form = []
        self.links = []
        self.tags = []
        self.height = []
        self.width = []
        for i in string:
            self.ids.append(i.split(',"created_at"')[0])
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
            self.tags.append(i.split('"tags":"')[1].split('"')[0].replace(", ", ",,"))
