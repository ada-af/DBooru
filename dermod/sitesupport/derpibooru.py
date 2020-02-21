query = "my:faves" # "my:upvotes"
api_key = "API-KEY GOES HERE"

# Do not change values below line 4
domain = 'https://derpibooru.org'
endpoint = "/api/v1/json/search/images?q={}".format(query)
paginator = "&page={}"
# Must be regexp
empty_page = '\{"images":\[\],"'
slp = 0.2 # Defines delay between requests
params = "&per_page=50&key={}".format(api_key)

class Module:
    import html
    import urllib.parse

    def __init__(self):
        self.tags = []
        self.ids = []
        self.links = []
        self.form = []
        self.height = []
        self.width = []

    def parse(self, string, pg_num):
        string = self.html.unescape(self.urllib.parse.unquote(string))
        string = string.split('interactions":[{"')[0]
        string = string.split('"format":')[1:]
        j = 0
        for i in string:
            try:
                width = i.split('"width":')[1]
                width = width.split(',')[0].strip("}{][")
                height = i.split('"height":')[1]
                height = height.split(',')[0].strip("}{][")
                form = i.split(',')[0].lower().strip('"')
                url = i.split('"full":"')[1]
                url = url.split('"')[0].strip("}{][")
                if '"tags":null' in i:
                    e = "Tag parsing error. Refer to github.com/mcilya/DBooru/issues/29"
                else:
                    e = i.split('"tags":[')[1]
                    e = e.split('],')[0]
                    f = [x.strip('"\'') for x in e.split(',')]
                    tags = ",,".join(f)
            except Exception:
                print("Derpibooru JSON API problem. Entry {} on page {} left unprocessed          ".format(j, pg_num))
            else:
                self.ids.append(i.split('"id":')[1].split(',')[0])
                self.width.append(width)
                self.height.append(height)
                self.form.append(form)
                self.links.append(url)
                self.tags.append(tags)    
            j += 1