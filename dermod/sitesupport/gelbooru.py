userid = "YOUR GELBOORU ID HERE"

# Do not change values below this line (aka line 3)

domain = 'https://gelbooru.com/index.php'
query = "{}".format(userid)
endpoint = "/index.php?page=favorites&s=view&id={}".format(query)
class paginator:
    def format(page):
        return "&pid={}".format(page*50-50)
empty_page = r'; //]]></script><div style="margin-top:' # Must be regexp
slp = 0.5 # Defines delay between requests
params = '' # Additional API params
# hard_limit = 750 # Max available page
from threading import Thread

class Module:
    import re

    def __init__(self):
        self.tags = []
        self.ids = []
        self.links = []
        self.form = []
        self.height = []
        self.width = []
    
    def parse(self, string):
        loc_thr = []
        string = self.re.findall("posts\[\d+\]", string)
        if len(string) == 0:
            return
        for i in string:
            i = i.split('[')[1].split(']')[0]
            t = Image(i)
            t.start()
            loc_thr.append(t)
        for i in loc_thr:
            if i.ready:
                self.tags.append(i.tags)
                self.ids.append(i.id)
                self.links.append(i.links)
                self.form.append(i.form)
                self.height.append(i.height)
                self.width.append(i.width)
        

class Image(Thread):
    import requests
    import json
    import settings_file

    def __init__(self, id):
        Thread.__init__(self)
        self.tags = ""
        self.id = id
        self.links = ""
        self.form = ""
        self.height = ""
        self.width = ""
        self.ready = False
        self._get_data()

    def _get_data(self):
        with self.requests.Session() as s:
            if self.settings_file.enable_proxy is False:
                raw_data = s.get(
                    "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id={id}".format(id=self.id),
                    verify=self.settings_file.ssl_verify, timeout=self.settings_file.time_wait)
            else:
                raw_data = s.get(
                    "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id={id}".format(id=self.id),
                    proxies=dict(
                        https='socks5://{}:{}'.format(
                            self.settings_file.socks5_proxy_ip, self.settings_file.socks5_proxy_port),
                        http='socks5://{}:{}'.format(self.settings_file.socks5_proxy_ip, self.settings_file.socks5_proxy_port)),
                    verify=self.settings_file.ssl_verify, timeout=self.settings_file.time_wait)
        json = self.json.loads(raw_data.text)
        self.links = json[0]['file_url']
        self.form = json[0]['image'].split(".")[-1]
        self.height = str(json[0]['height'])
        self.width = str(json[0]['width'])
        self.tags = str(json[0]['tags'])
        self.ready = True