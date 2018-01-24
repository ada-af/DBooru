# General Info
# NEVER DELETE/SET TO WRONG FORMAT OR LEAVE VARIABLES EMPTY! OTHER WAY EVERYTHING WILL FUCK UP!


# Define modules to work with
# Module name is case sensetive
# Available modules placed in dermod/sitesupport
# Some modules may require changing settings
# Format: modules = list(string, string)
# Example: (modules = ['derpibooru', 'e621'])
modules = ['derpibooru']

# Output Errors
# There will be over 9000 errors. Do not set False unless you are developer or someone who know programming
# Format: suppress_errors = bool # Example: (suppress_errors = True)
suppress_errors = True

# Disable requests verifying
# Useful when connecting to derpibooru through tor
# Format: ssl_verify = bool or string
# Example: Enable verification (ssl_verify = True)
# Example: Disable verification (ssl_verify = False)
# Example: Use custom CA Cert (ssl_verify = 'cacert.pem')
ssl_verify = True

# Proxy Settings
# Useful if connection to derpibooru is blocked by anything

# Enable proxy for connections
# Format: enable_proxy = bool
# Example: (enable_proxy = True)
enable_proxy = False


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


# Database specific settings

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
discover_servers = False

# Turns on/off sharing images in lan
# Format: discover_servers = bool
# Example: (share_images = False)
share_images = False


# Following settings

# Enable or Disable running follower with webUI
# Format: run_follower = bool
# Example: (run_follower = False)
run_follower = False

# Defines amount of pages to check
# Format: checked_pages = int
# Example: (checked_pages = 10)
checked_pages = 25

# Defines time between checking again
# Format: follower_sleep = int
# Example: (follower_sleep = 600) # Checks every 600 seconds = 10 minutes
follower_sleep = 1800


# Threading

# Defines maximum running threads before waiting before creating new threads
# Format: thread_cap = int
# Example: (thread_cap = 200) # New threads will be created with delay after reaching this value
thread_cap = 50

# Defines time to wait after reaching thread cap
# Format: sleep_time = int
# Example: (sleep_time = 5) # Will wait 5 seconds before creating new thread
sleep_time = 5


# DO NOT CHANGE #
# Due to some serious shit never change these settings or everything will fuck up.
suppressor = suppress_errors
columns = ['fname']
# DO NOT CHANGE #
