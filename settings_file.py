# General Info
# NEVER DELETE/SET TO WRONG FORMAT OR LEAVE VARIABLES EMPTY! OTHER WAY EVERYTHING WILL FUCK UP!
import os

# Define modules to work with
# Module name is case sensetive
# Available modules placed in dermod/sitesupport
# Some modules may require changing settings
# Format: modules = list(string, string)
# Example: (modules = ['derpibooru', 'e621'])
modules = ['derpibooru']

# General settings

# Hide Errors
# There will be over 9000 errors. 
# Do not set False unless you are developer or someone who knows programming
# Options: [True, False]
# Format: suppress_errors = bool 
# Example: (suppress_errors = True)
suppress_errors = True

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
# Format: THREADS_PER_PAGE = int
# Example: THREADS_PER_PAGE = 4
THREADS_PER_PAGE = 2

# Enable debugging
# Options: [True, False]
# Format: debugging = bool
# Example: (debugging = True)
debugging = False

# Disable requests verifying
# Useful when connecting to derpibooru through tor
# Format: ssl_verify = bool or string
# Require example
# Example: Enable verification (ssl_verify = True)
# Example: Disable verification (ssl_verify = False)
# Example: Use custom CA Cert (ssl_verify = '/etc/cacert.pem')
ssl_verify = True

# Proxy Settings
# Useful if connection to derpibooru is blocked by anything

# Enable proxy for connections
# Options: [True, False]
# Format: enable_proxy = bool
# Example: (enable_proxy = True)
enable_proxy = False

# Proxy server type
# Format: proxy_type = string
# Options: ['http', 'socks4', 'socks5', 'socks5h']
proxy_type = 'http'

# IP address of proxy server
# Format: proxy_ip = string
# Require example
# Example: Without auth (proxy_ip = "127.0.0.1")
# Example: With auth (proxy_ip = "user@passwd:127.0.0.1")
proxy_ip = "127.0.0.1"

# Port used by proxy server
# Format: proxy_port = string
# Example: (proxy_port = "9050")
proxy_port = "9050"


# WEB interface

# Defines ip where to bind webUI
# Format: web_ip = string
# Example: web_ip = "127.0.0.1"
web_ip = "0.0.0.0"

# Defines port where to bind webUI
# Format: web_port = int
# Example: web_port = 1337
web_port = 9000

# Defines whether tag prediction should be disabled in webUI
# Options: [True, False]
# Format: disable_mobile = Bool
# Example: disable_mobile = True
disable_mobile = False

# Defines how many tags to show when predicting
# Format: predict_tags = int
# Example: predict_tags = 50
predict_tags = 20

# Defines if thumbnails must be kept
# Only works with ffmpeg thumbnailer
# Options: [True, False]
# Format: keep_thumbs = bool
# Example: keep_thumbs = True
keep_thumbs = False

# Defines tool to make thumbnails
# Can be "disabled", "ffmpeg" or "PIL"
# Options: ["disabled", "ffmpeg", "PIL"]
# Format: thumbnailer = string
# Example: thumbnailer = "PIL"
thumbnailer = "ffmpeg"

# Defines how many pictures must be shown in output
# Format: showing_imgs = int
# Example: showing_imgs = 5
showing_imgs = 20

# Ffmpeg settings

# Format to use when generating thumbnail for images
# Can be any format supported by ffmpeg
# Only works if thumbnailer set to "ffmpeg"
# Format: conv_format = string
# Example: conv_format = "webp"
conv_format = "mjpeg"

# Additional parameters for ffmpeg
# Only works if thumbnailer set to "ffmpeg"
# I don't have an idea why would you need to add something, but let it be
# Currently hides all output from ffmpeg
# Format: ffmpeg_args = string
# Example: ffmpeg_args = "-loglevel quiet -vf 'noise=alls=25:allf=u+t'"
ffmpeg_args = "-loglevel quiet"

# Should gif thumbnails be converted to webp
# Only works if thumbnailer set to "ffmpeg"
# Options: [True, False]
# Format: gif_to_webp = Bool
# Example: gif_to_webp = True
gif_to_webp = False


# Database specific settings

# Defines if mysql connection should be used
# Format: use_mysql = bool
# Options: [True, False]
# Example: use_mysql = True
use_mysql = False

# Defines mysql user
# Format: mysql_user = string
# Example: mysql_user = "someuser"
mysql_user = "user"

# Defines mysql password
# Format: mysql_password = string
# Example: mysql_password = "123456"
mysql_password = "hunter2"

# Defines name (or path and name) for database file
# Format: db_name = string
# Require example
# Example: (db_name = "sqlite.db" or db_name = "C:/User/sqlite.db")
# Example: (db_name = "sqlite.db" or db_name = "/home/vasyan/sqlite.db")
# In case of using mysql defines schema name
# Example: (db_name = "images")
db_name = "sqlite.db"

# Defines maximum amount of tags to show in search query
# Does nothing for web version
# Format: showing_tags = int
# Example: (showing_tags = 14)
showing_tags = 15


# Path settings

# Defines path where to store downloaded images
# Supports relative and full paths
# Format: images_path = string
# Require example
# Example: (images_path = "./images/" or image_path = "C:/User/Images/")
# Example: (images_path = "./images/" or image_path = "/home/vasyan/images/")
images_path = "./images/"

# Defines path where images should be exported to
# Format: export_path = string
# Require example
# Example: (export_path = "./images_exp/" or export_path = "C:/User/Images_exp/")
# Example: (export_path = "./images_exp/" or export_path = "/home/vasyan/images_exp/")
export_path = "./exported/"

# Defines name (or path and name) for temporary file
# Format: ids_file = string
# Require example
# Example: (ids_file = "img_ids.txt" or ids_file = "C:/User/Temp/Filename.dat")
# Example: (ids_file = "img_ids.txt" or ids_file = "/home/vasyan/img_ids.txt")
ids_file = "img_ids.txt"

# Defines path where thumbnails will be stored
# Format: thumbs_path = string
# Require example
# Example: (thumbs_path = "./thumbs/" or thumbs_path = "C:/User/vasyan/thumbs/")
# Example: (thumbs_path = "./thumbs/" or thumbs_path = "/home/vasyan/thumbs/")
thumbs_path = "./thumbs/"


# Threading

# Defines thread lifespan
# Format: wait_time = int
# Example: (time_wait = 10)
time_wait = 60

# Defines maximum running threads before waiting before creating new threads
# Format: thread_cap = int
# Example: (thread_cap = 200) # New threads will be created with delay after reaching this value
thread_cap = 50

# Defines time to wait after reaching thread cap
# Format: sleep_time = int
# Example: (sleep_time = 5) # Will wait 5 seconds before creating new thread
sleep_time = 5

# Enables/disables checks for changes in settings_file.py
# Options: [True, False]
# Format: polling_time = bool
# Example: polling_time = False
enable_polling = False


# Defines time (in seconds) between checks for changes in settings_file.py
# Format: polling_time = int
# Example: polling_time = 60
polling_time = 10


# First run

# Show /settings page on next start 
# Automatically disabled after start
# Options: [True, False]
# Format: first_run = bool
# Example: first_run = False
first_run = False