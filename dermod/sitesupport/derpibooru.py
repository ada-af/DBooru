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
    import json

    def __init__(self):
        self.tags = []
        self.ids = []
        self.links = []
        self.form = []
        self.height = []
        self.width = []

    def parse(self, string, pg_num):
        string = string.split('interactions":[{"')[0]
        string = string.split('"id":')[1:]
        j = 0
        for i in string:
            try:
                k = i.split('"width":')[1]
                a = k.split(',')[0]
                k = i.split('"height":')[1]
                b = k.split(',')[0]
                k = i.split('original_format')[1]
                c = k.split('":"')[1].split('","')[0]
                k = i.split('","full":"')[1]
                k = k.split('","webm":"')[0]
                d = k.split('"},"is_rendered"')[0].replace("//", "https://")
                e = i.split('"tags":"')[1].split('",')[0].replace(", ", ",,")
            except Exception:
                print("Derpibooru JSON API problem. Entry {} on page {} left unprocessed          ".format(j, pg_num))
            else:
                self.ids.append(i.split(',"created_at"')[0])
                self.width.append(a)
                self.height.append(b)
                self.form.append(c)
                self.links.append(d)
                self.tags.append(e)    
            j += 1
