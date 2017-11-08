# General Info
# NEVER DELETE/SET TO WRONG FORMAT OR LEAVE VARIABLES EMPTY! OTHER WAY EVERYTHING WILL FUCK UP!


# Api Key
# Can be found here: https://derpibooru.org/users/edit
# Looks like: "R5bBvcs788sds86j327D"
# Format: user_api_key = string
# Example: (user_api_key = "R5bBvcs788sds86j327D")
user_api_key = "KEY GOES HERE"

# Output Errors
# There will be over 9000 errors. Do not set False unless you are developer or someone who know programming
# Format: suppress_errors = bool # Example: (suppress_errors = True)
suppress_errors = False

# Disable requests verifying
# Useful when connecting to derpibooru through tor
# Format: ssl_verify = bool or string
# Example: Enable verification (ssl_verify = True)
# Example: Disable verification (ssl_verify = False)
# Example: Use custom CA Cert (ssl_verify = 'cacert.pem')
ssl_verify = True

# Set derpibooru domain
# Format: domain = string
# Example: (domain = "trixiebooru.org")
domain = "derpibooru.org"

# Proxy Settings
# Useful if connection to derpibooru is blocked by anything

# Enable proxy for connections to derpibooru.org itself
# Format: enable_proxy = bool
# Example: (enable_proxy = True)
enable_proxy = False

# Enable proxy for connections to derpicdn.net
# Sometimes derpibooru.org is blocked, but derpicdn is freely accessible
# Format: derpicdn_enable_proxy = bool
# Example: (derpicdn_enable_proxy = True)
derpicdn_enable_proxy = False


# Proxy IP/Port Settings

# You know what to do. I guess...
# Format: socks5_proxy_ip = string
# Example: (socks5_proxy_ip = "127.0.0.1")
socks5_proxy_ip = "127.0.0.1"

# Format: socks5_proxy_port = string
# Example: (socks5_proxy_port = "9050")
socks5_proxy_port = "9050"


# WEB interface

# Defines ip where to bind webUI
# Format: web_ip = string
# Example: web_ip = "127.0.0.1"
web_ip = "0.0.0.0"

# Defines port where to bind webUI
# Format: web_port = int
# Example: web_port = 1337
web_port = 9000


# Derpibooru/database specific settings

# Defines if download only favorited or both upvoted and favorited
# Format: vote = string
# Example: (vote = "faves")
vote = "upvotes"

# Defines how many "Tag*" fields database must have
# Format: tag_amount = int
# Example: (tag_amount = 40)
tag_amount = 40

# Defines how many pictures must be shown in output
# Format: showing_imgs = int
# Example: showing_imgs = 5
showing_imgs = 15

# Defines maximum amount of tags to show in search query
# Format: showing_tags = int
# Example: (showing_tags = 14)
showing_tags = 15


# Path settings

# Defines path where to store downloaded images
# Supports relative and full paths
# Format: images_path = string
# Example_windows: (images_path = "./images/" or image_path = "C:/User/Images/")
# Example_linux: (images_path = "./images/" or image_path = "/home/vasyan/images/")
images_path = "./images/"

# Defines path where images should be exported to
# Format: export_path = string
# Example_windows: (export_path = "./images_exp/" or export_path = "C:/User/Images_exp/")
# Example_linux: (export_path = "./images_exp/" or export_path = "/home/vasyan/images_exp/")
export_path = "./exported/"

# Defines thread lifespan
# Format: wait_time = int
# Example: (time_wait = 10)
time_wait = 15

# Defines name (or path and name) for temporary file
# Format: ids_file = string
# Example_windows: (ids_file = "img_ids.txt" or ids_file = "C:/User/Temp/Filename.dat")
# Example_linux: (ids_file = "img_ids.txt" or ids_file = "/home/vasyan/img_ids.txt")
ids_file = "img_ids.txt"

# Defines name (or path and name) for database file
# Format: db_name = string
# Example_windows: (db_name = "sqlite.db" or db_name = "C:/User/sqlite.db")
# Example_linux: (db_name = "sqlite.db" or db_name = "/home/vasyan/sqlite.db")
db_name = "sqlite.db"

# Sets database main table name. Usually no need to change it
# Format: table_name = string
# Example: (table_name = 'images')
table_name = 'images'


# Servers discovery options

# Turns on/off local servers discovery
# Format: discover_servers = bool
# Example: (discover_servers = False)
discover_servers = True

# Turns on/off sharing images in lan
# Format: discover_servers = bool
# Example: (share_images = False)
share_images = True

# NOT IMPLEMENTED {
#
# Defines name (or path and name) for temporary follow file
# Format: follow_file = string
# Example_windows: (follow_file = "follow_ids.txt" or follow_file = "C:/User/Temp/Filename.dat")
# Example_linux: (follow_file = "follow_ids.txt" or follow_file = "/home/vasyan/follow_ids.txt")
# follow_file = "follow_ids.txt"
#
# }

# DEPRECATED {
#
# Defines how many pages should be checked
# Format: pages_num = int
# Example: (pages_num = 500)
# pages_num = 1000
#
#
# Defines how many threads can be used for downloading images
# Do not set values bigger than 30 while using tor
# Format: max_threads = int
# Example: (max_threads = 15)
# max_threads = 30
# }

# DO NOT CHANGE #
# Due to some serious shit never change these settings or everything will fuck up.
suppressor = suppress_errors
columns = ['fname']
# DO NOT CHANGE #
