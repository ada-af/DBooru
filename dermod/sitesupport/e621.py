username = "YOUR USERNAME GOES HERE"

# Do not change values below this line (aka line 3)

domain = 'https://e621.net'
query = "fav:{}".format(username)
endpoint = "/posts.json?tags={}".format(query)
paginator = "&page={}"
empty_page = '\{"posts":\[\]\}' # Must be regexp
slp = 1 # Defines delay between requests
params = '&limit=320' # Additional API params
hard_limit = 750 # Max available page

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

    def parse(self, string):
        string = self.html.unescape(self.urllib.parse.unquote(string))
        string = string.split('"posts":')[1]

        for i in string.split("},{"):
            self.ids.append(i.split('"id":')[1].split(',')[0])
            r = i.split('"rating":"')[1][0]
            if r == "e":
                r = "explicit"
            elif r == "q":
                r = "questionable"
            elif r == "s":
                r = "safe"

            tags = []

            t_tags = i.split('"tags":')[1].split("}")[0].split("],")
            for j in t_tags:
                if j.startswith('"artist"'):
                    j = ["artist:"+x.replace("_", " ") for x in j.split(":[")[1].strip('"').split('","')]
                else:
                    j = [x.replace("_", " ") for x in j.split(":[")[1].strip('"').split('","')]
                if j != [''] and j != [']']:
                    tags += j

            k = r + ",," + ",,".join(sorted(tags))
            self.tags.append(k)

            k = i.split('"file":')[1]

            j = k.split('"width":')[1]
            j = j.split(',')[0]
            self.width.append(j)
            j = k.split('"height":')[1]
            j = j.split(',')[0]
            self.height.append(j)
            ext = k.split('ext":"')[1]
            ext = ext.split('"')[0]
            self.form.append(ext)
            try:
                j = k.split('"url":"')[1]
                j = j.split('"')[0]
            except: 
                # Either they broke everything or they won't show links for some images for some reason
                # Whatever it is im generating urls by myself ¯\_(ツ)_/¯ 
                j = k.split('"md5":"')[1]
                j = j.split('"')[0]
                j = "https://static1.e621.net/data/{st}/{nd}/{md5}.{form}".format(st=j[0:2], nd=j[2:4], md5=j, form=ext)
            self.links.append(j)
