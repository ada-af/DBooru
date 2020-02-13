username = "YOUR USERNAME GOES HERE"

# Do not change values below this line (aka line 3)

domain = 'https://yande.re'
query = "vote:3:{}".format(username)
endpoint = "/post.json?tags={}".format(query)
paginator = "&page={}"
empty_page = '\[\]$' # Must be regexp
slp = 0.5 # Defines delay between requests
params = '&limit=100' # Additional API params
# hard_limit = 750 # Max available page

class Module:
    def __init__(self):
        self.tags = []
        self.ids = []
        self.img_links = []
        self.format = []
        self.height = []
        self.width = []

    def parse(self, string):
        string = string.replace("%20", ' ').split('"id":')[1:]
        self.ids = []
        self.form = []
        self.links = []
        self.tags = []
        self.height = []
        self.width = []
        for i in string[1:]:
            self.ids.append(i.split(',"')[0])
            r = i.split('"rating":"')[1][0]
            if r == "e":
                r = "explicit"
            elif r == "q":
                r = "questionable"
            elif r == "s":
                r = "safe"
            k = i.split('"tags":"')[1]
            k = k.split('",')[0]
            k = k.replace(" ", ',,')
            k = k.replace('_', ' ')
            k = r + ",," + k 
            self.tags.append(k)
            k = i.split('"width":')[1]
            k = k.split(',')[0]
            self.width.append(k)
            k = i.split('"height":')[1]
            k = k.split(',')[0]
            self.height.append(k)
            k = i.split('file_ext":"')[1]
            k = k.split('",')[0]
            self.form.append(k)
            k = i.split('"file_url":"')[1]
            k = k.split('",')[0]
            self.links.append(k)
