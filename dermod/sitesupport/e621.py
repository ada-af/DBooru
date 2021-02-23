from time import sleep
import dermod


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
max_checkers = 2

class Module:
    import html
    import urllib.parse

    def __init__(self):
        self._init_db()
        self.tags = []
        self.ids = []
        self.links = []
        self.form = []
        self.height = []
        self.width = []

    def parse(self, string):
        from .helpers import get_resource
        from . import logger
        import time
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
            self.tags.append(k.replace('[', '').replace(']', ''))

            if (len((pools := i.split('"pools":[')[1].split('],')[0].split(','))) > 0) and pools != ['']:
                for j in pools:
                    if (pool_name := self.check_pool(j)) is False:
                        self.remember_pool(j, "")
                        time.sleep(slp*1.5) # Fuck you e621. Make an API that works like an API
                        logger.debug(f"Checking pool #{j} // Triggered by e621 image: {self.ids[-1]}")
                        print(f"Checking pool #{j} // Triggered by e621 image: {self.ids[-1]}\n")
                        data = get_resource("https://e621.net//pools/{}.json".format(j.strip())).content.decode()
                        pool_name = data.split("name\":\"")[1].split("\",")[0].replace('\'', '').replace('"', '').replace('_', ' ')
                        self.remember_pool(j, pool_name)
                    if pool_name == "":
                        while pool_name == "":
                            pool_name = self.check_pool(j)
                            time.sleep(0.5)
                    self.tags.append(f"pool:{pool_name}")
                        

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

    def _init_db(self):
        import settings_file
        from dermod.db import init_db
        conn, cursor = init_db()
        if settings_file.use_mysql:
            cursor.execute("SHOW TABLES")
            t = [x[0] for x in cursor.fetchall()]
        else:
            t = [x[1] for x in cursor.execute("select * from sqlite_master").fetchall()]
        if "e621_pools" not in t:
            cursor.execute("CREATE TABLE e621_pools(id int, pool_name text, PRIMARY KEY (id))")
        cursor.execute("delete from e621_pools where pool_name = \"\"")
        conn.commit()
        conn.close()

    def remember_pool(self, id, name):
        from dermod.db import init_db
        import settings_file
        conn, cursor = init_db()

        if settings_file.use_mysql:
            cursor.execute("REPLACE INTO e621_pools values (%s, %s)", (id, name))
        else:
            cursor.execute("REPLACE INTO e621_pools values (?, ?)", (id, name))
        conn.commit()
        conn.close()
        
    def check_pool(self, id):
        from dermod.db import init_db
        import settings_file
        conn, cursor = init_db()
        
        if settings_file.use_mysql:
            cursor.execute("select pool_name from e621_pools where id = %s", [id])
        else:
            cursor.execute("select pool_name from e621_pools where id = ?", [id])
        pool_name = cursor.fetchone()
        conn.close()


        return pool_name[0] if pool_name else False