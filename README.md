# DBooru

<!-- TOC -->

- [DBooru](#dbooru)
  - [Branching](#branching)
    - [Master](#master)
    - [Next or any other branch](#next-or-any-other-branch)
  - [Features](#features)
    - [Both versions](#both-versions)
    - [Web-Interface](#web-interface)
    - [CLI-Version](#cli-version)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
    - [Configuration](#configuration)
    - [How to run](#how-to-run)
      - [CLI](#cli)
      - [Web](#web)
  - [Modules](#modules)
    - [Why do i need modules?](#why-do-i-need-modules)
    - [I want more modules!](#i-want-more-modules)
    - [Are you kidding me?](#are-you-kidding-me)
      - [Examples](#examples)
  - [Commands and Web-endpoints](#commands-and-web-endpoints)
    - [CLI](#cli-1)
      - [Main menu](#main-menu)
      - [Search](#search)
    - [Web](#web-1)
  - [Search basics and syntax](#search-basics-and-syntax)
    - [Basic search rules](#basic-search-rules)
    - [Special tags](#special-tags)
      - [Syntax](#syntax)
  - [Settings_file.py](#settingsfilepy)
  - [dermod/aliases.py](#dermodaliasespy)
    - [Syntax](#syntax-1)

<!-- /TOC -->

## Branching

### Master

1. Stable branch
1. Rare updates
1. Lots of changes per update

### Next or any other branch

1. Unstable
1. Lots of commits
1. Lots of updates
1. New features
1. Broken old features
1. Rare commit messages
1. If there a commit message then "Minor changes"*  
    *Minor changes may include removal of half of all code

## Features

### Both versions

1. Search in downloaded images
    1. By tags
    2. By image dimensions
2. Viewing images
3. Loading images from *booru
    1. Even with proxy (socks5 only)

### Web-Interface

1. Downloading images
1. Exporting images
1. Tag predictions
1. Change page with ← or → arrows
1. Scroll through images with ← or → arrows

### CLI-Version

¯\\\_(ツ)_/¯
> To be deprecated


## Installation

### Dependencies

>- Python 3.5+ or PyPy3 5.9.0+
>- pip
>- requests
>- requests[security]
>- pysocks
>- idna
>- cryptography
>- ffmpeg or pillow
>- flask
>- jinja2
>- werkzeug
>- markupsafe
>- click
>- itsdangerous
>
>Or you can just type `pip install --user -r requirements.txt` in terminal

### Configuration

1. Set modules (line 11) in settings_file.py
2. Configure modules (placed in dermod/sitesupport)
3. (Optionally) Change other settings (View [Settings_file.py](#settings_filepy))

### How to run

#### CLI

1. Run `python main.py` or `pypy3 main.py`
1. Type in "get images"
1. Wait for images to download
1. Use search
1. ???
1. PROFIT

#### Web

1. Run `python DBooru_web.py` or `pypy3 DBooru_web.py`
1. Press `Update DB` button
1. Wait for images to download
1. Use search
1. ???
1. PROFIT

## Modules

### Why do i need modules?

Modules allows you to configure DBooru for using with multiple *booru without rewriting half of code

### I want more modules!

Open issue with site name and module description **OR** Write your own module

### Are you kidding me?

It's not too hard (if site uses api ofc), you can use included modules as example.

Module must contain:

1. Configurable options
1. Site domain
1. Search query
1. Search endpoint
1. Paging parameter
1. Empty page delimiter
1. Additional parameters (such as API-key parameter)
1. Hard limit
1. Parser Configuration

#### Examples

    Configurable options
    >> username = "NAME GOES HERE"
    >> apikey = "KEY"

    Site Domain
    >> domain = "https://example.com"

    Search query [Can be configurable]
    >> query = "likedby:{}".format(username) [Preferred variant]
    >> query = "sky, ponies" [Well, if you gonna download pictures with this tags only, then it's ok]

    Search endpoint (Varies depending on site)
    >> endpoint = "/search?q={}".format(query)
    >> endpoint = "/tags/{}".format(query)

    Paging parameter (Varies depending on site)
    >> paginator = "&page={}"
    >> paginator = "&p={}"
    >> paginator = "/{}"

    In case of overly specific pagination can be implemented as class (check gelbooru module)
    >> class paginator:
    >>    def format(page):
    >>        return "/pg/{}".format(page*25)

    Empty page delimiter (Varies depending on site)
    > RegExp matching page with no images
    >> empty_page = "\[\]$"
    >> empty_page = "{images:\[\]"

    Sleep time (to get rid of rate limiting)
    > Value must be int or float
    >> slp = 1
    >> slp = 0.5

    Additional params
    > Such as api keys
    >> params = '&key={}&username={}'.format(apikey, username)

    Hard limit (for when your life is not limited enough)
    >Use if api does not allow requesting pages after N
    >tip: this is not mandatory, but if you don't want to be banned specify this
    >> hard_limit = 750 [notice, this time we're not using quotes]

    Parser Configuration
    May use whatever python functions/packages you want to use (check gelbooru module)
    MUST start with and MUST contain parse(self, string) method
    >> class Module:
    >>    def __init__(self):
    >>        self.tags = []
    >>        self.ids = []
    >>        self.links = []
    >>        self.form = []
    >>        self.height = []
    >>        self.width = []  


    Parse() method
    Response from server passed with string argument
    If page number required `pg_num` added to input arguments
      Note: pg_num receives raw page number (1, 2, 3, ...)
    >>    def parse(self, string): 
    >>    # here goes parsing
    >>    # ...
    >>    # parsed values must be added to lists
    >>    for i in parsed_values:
    >>      self.tags.append(i[0]) # tags MUST be delimited by `,,`
    >>      self.ids.append(i[4])
    >>      self.links.append(i[3])
    >>      self.form.append(i[5])
    >>      self.height.append(i[2])
    >>      self.width.append(i[1])

## Commands and Web-endpoints

### CLI

#### Main menu

Enter this commands if prompt starts with `DB>`

| Command            | Description                                                |
| ------------------ | ---------------------------------------------------------- |
| help               | Shows in-app help                                          |
| get images         | Downloads images that you liked/favorited on *booru        |
| get images --force | Downloads images without checking if file exists           |
| total              | Prints amount of entries in local DB                       |
| count \<tag\>      | Prints amount of entries tagged with \<tag\>               |
| show \<image_id>   | Opens image in image viewer or browser if no viewers found |
| quit (exit)        | Closes app                                                 |
| \<anything>        | Uses input as list of tags and searches for it             |

#### Search

Enter this commands if prompt starts with `Search@DB>`

| Command          | Description                                                |
| ---------------- | ---------------------------------------------------------- |
| show \<image_id> | Opens image in image viewer or browser if no viewers found |
| quit (exit)      | Closes app                                                 |
| back             | Returns to main menu                                       |
| \<any_number>    | Show page numbered as \<any_number>                        |
| \<anything>      | Uses input as list of tags and searches for it             |

### Web

|         Endpoint          | Method | Parameters (Body for POST)      | Description                                       | Returns                                                                                                  |
| :-----------------------: | :----: | ------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
|            "/"            |  GET   |                                 | Main page                                         | HTML-page                                                                                                |
|         "/search"         |  GET   | q=**search_query** page=**int** | Search images                                     | HTML-page                                                                                                |
|     "/image/**str**"      |  GET   |                                 | View image with tags                              | HTML-page                                                                                                |
|    "/dl/**filename**"     |  GET   |                                 | Browser-friendly download method                  | Image                                                                                                    |
|    "/raw/**filename**"    |  GET   |                                 | Raw image data                                    | Image                                                                                                    |
|        "/predict"         |  GET   | phrase=**search_query**         | Tries to predict search query                     | Plain text data                                                                                          |
|      "/next/**str**"      |  GET   |                                 | Tries to get id of next (newer) image             | Redirect (302) to /image/\*                                                                              |
|    "/previous/**str**     |  GET   |                                 | Tries to get id of previous(older) image          | Redirect (302) to /image/\*                                                                              |
| "/thumbnail/**filename**" |  GET   |                                 | Makes thumbnail (500px) of image (returns full image if thumbnailer disabled)                  | Image                                                                                                    |
|      "/json/search"       |  GET   | q=**query** page=**int**        | Searches images and returns json result of search | JSON                                                                                                     |
|         "/random"         |  GET   |                                 | Redirects to random image                         | Redirect (302) to /image/\*                                                                              |
|     "/random/**tags**     |  GET   |                                 | Redirects to random image tagged with **tags**    | Redirect (302) to /image/\*                                                                              |
|         "/update"         |  GET   |                                 | Updates DB (Same as CLI: get images)              | Returns 200 code when update started successfully or 409 in case when there's already update in progress |

## Search basics and syntax

### Basic search rules

1. Wildcard through **`*`** (asterisk)

>Example: "ti`*`" will return images where at least one tag starts with `ti`
2. Tags must be separated by **`,`** (comma)
>Example: "safe`,` princess luna"
3. Tags are not case sensitive
>Example: "SaFe" == "SafE" == "safe"
4. Search for "tag" will only return images tagged with "tag" not "tag*"
>Example: "`safe`" returns images with tag "safe" and doesn't returns "safezone"
5. Searching multiple tags will return images matching all the tags
>Example: "`safe, princess luna`" will return images tagged with both "safe" and "princess luna"
6. Exclude tags by placing **`-`** (hyphen-minus) before tag
>Example: "`-safe`" returns all images not tagged with "safe"
7. OR queries will return images tagged with tag1 or tag2
>Example: "`(fluttershy|applejack)`" returns images tagged with `fluttershy`, `applejack` or both tags
8. OR queries could be mixed with AND queries
>Example: "`safe,(princess luna|changeling)`" returns images tagged `princess luna, safe` or `changeling, safe`
9. Exclusion is not supported for OR queries. It's just pointless.
10. Rules 1,3,4,5 work almost the same for exclude

### Special tags

>Works only for filtering searches
>
>Example: `width=100` works, while `-width=100` doesn't work

1. `height`
2. `width`
3. `ratio`

#### Syntax

1. **`=`** or **`==`** means equal to \<value>
1. **`!=`** or **`<>`** means not equal to \<value>
1. **`>`** means bigger than \<value>
1. **`<`** means less than \<value>
1. **`>=`** means bigger or equal to \<value>
1. **`<=`** means less or equal to \<value>

>Example: 'safe, width>100" will return images tagged with 'safe' tag and image with width bigger than 100px

## Settings_file.py

| Option            | Format                                      | Description                                                                 |
| ----------------- | ------------------------------------------- | --------------------------------------------------------------------------- |
| modules           | List (['String', 'String'])                 | Enables modules                                                             |
| suppress_errors   | Bool (True/False)                           | Prints errors and stacktrace in case of happening                           |
| ssl_verify        | Bool (True/False) or String ("Path")        | Enable/Disable ssl verification or set custom CA Cert                       |
| enable_proxy      | Bool (True/False)                           | Enables/Disables proxy for requests                                         |
| socks5_proxy_ip   | String (IP)                                 | Sets proxy IP                                                               |
| socks5_proxy_port | String (Port)                               | Sets proxy port                                                             |
| BASE_DIR          | Function                                    | Magic for flask to work                                                     |
| web_ip            | String (IP)                                 | Set IP to bind Web interface                                                |
| web_port          | Integer (port)                              | Sets port to bind Web interface                                             |
| thumbnailer       | String (One of "ffmpeg", "PIL", "disabled") | Defines tool to make thumbnails or not to make them at all                  |
| conv_format       | String (ffmpeg output format)               | Format to use when making thumbnails                                        |
| ffmpeg_args       | String (ffmpeg parameters)                  | For situations when you think that default settings suck                    |
| gif_to_webp       | Bool (True/False)                           | Creates webp thumbnails for gifs                                            |
| disable_mobile    | Bool (True/False)                           | Should tag prediction be disabled on mobile                                 |
| predict_tags      | Integer (number)                            | How many tags to show when predicting input                                 |
| showing_imgs      | Integer (number)                            | How many images to show per page                                            |
| showing_tags      | Integer (number)                            | How many tags to **show** per image (CLI-only)                              |
| images_path       | String (Path)                               | Where to store loaded images                                                |
| export_path       | String (Path)                               | Where to store exported images                                              |
| time_wait         | Integer (seconds)                           | How long thread can stay alive                                              |
| ids_file          | String (Path/Filename)                      | Name for tempfile (No need to change)                                       |
| db_name           | String (Path/Filename)                      | Where to store DB file                                                      |
| thread_cap        | Integer (number)                            | Defines maximum running threads before blocking creating new threads        |
| sleep_time        | Integer (seconds)                           | Defines time to wait before creating new thread after thread cap is reached |
| enable_polling    | Bool                                        | Setting for enabling/disabling polling for changes in settings_file.py      |
| polling_time      | Integer (seconds)                           | Defines time (in seconds) between checks for changes in settings_file.py    |

## dermod/aliases.py

Allows creating alias to tag, so you can find one tag using alias

>Note: Aliasing alias won't work

### Syntax

```python
  aliases = {
      "alias1": "aliased tag1",
      "alias2": "aliased tag1",
      "alias3": "aliased tag2"
  }
```