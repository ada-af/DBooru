# DBooru

<!-- TOC -->

- [DBooru](#dbooru)
    - [Branching](#branching)
        - [Master](#master)
        - [Next](#next)
        - [Exp/Fixes/Test](#expfixestest)
    - [Features](#features)
        - [Both versions](#both-versions)
        - [CLI-version](#cli-version)
        - [Web-Interface](#web-interface)
    - [Installation](#installation)
        - [Dependencies](#dependencies)
        - [Configuration](#configuration)
        - [How to run](#how-to-run)
        - [How to make executable file](#how-to-make-executable-file)
    - [Modules](#modules)
        - [Why do i need modules?](#why-do-i-need-modules)
        - [I want more modules!](#i-want-more-modules)
        - [Are you kidding me?](#are-you-kidding-me)
            - [Examples](#examples)
    - [Commands and Web-endpoints](#commands-and-web-endpoints)
        - [CLI](#cli)
            - [Main menu](#main-menu)
            - [Search](#search)
        - [Web](#web)
    - [Search basics and syntax](#search-basics-and-syntax)
        - [Basic search rules](#basic-search-rules)
        - [Special tags](#special-tags)
            - [Syntax](#syntax)
    - [Settings_file.py](#settings_filepy)
    - [dermod/aliases.py](#dermodaliasespy)
        - [Syntax](#syntax-1)
    - [dermod/follow.py](#dermodfollowpy)

<!-- /TOC -->

## Branching
### Master

1. Stable branch
1. Rare updates
1. Lots of changes per update

### Next

1. Very unstable
1. Lots of commits
1. Lots of updates
1. New features 
1. Broken old features
1. Rare commit messages
1. If there a commit message then "Minor changes"*  
    *Minor changes may include removal of half of all code

### Exp/Fixes/Test

1. If there brach like Exp/Fixes/Test then only working branch is [Master](#master)
1. Nothing works
1. Lots of commits
1. Contains something new or fixes

## Features
### Both versions
1. Search in downloaded images
    1. By tags
    1. By image dimensions
1. Viewing images
### CLI-version
1. Loading images from *booru
    1. Even with proxy (socks5 only)

### Web-Interface
1. Downloading images
1. Exporting images
1. Tag predictions
1. Change page with ← or → arrows
1. Scroll through images with ← or → arrows


## Installation
### Dependencies
>- Python 3.4+ or PyPy3 5.9.0+
>- pip
>- requests
>- requests[security]
>- pysocks
>- idna
>- cryptography
>- ffmpeg or pillow
>
>If you have PyOpenSSL installed - remove it
>
>Or you can launch extra/linux\_deps.sh or extra/windows\_deps.bat and wait for magic

### Configuration
1. Set modules (line 11) in settings_file.py
1. Configure modules (placed in dermod/sitesupport)
1. (Optionally) Change other settings (View [Settings_file.py](#settings_filepy))

### How to run
1. Run `python main.py` or `pypy3 main.py`
1. Type in "get images"
1. Wait
1. Search or run `python webv3.py` or `pypy3 webv3.py`
1. ???
1. PROFIT

### How to make executable file

Run `python setup.py build`  
Executables will be placed in build/exe.(platform)-(python_version)/

>If you want to move executable be sure to move all the files in directory

If you want to change settings after building executable 
1. Rename `settings_file.py` to `settings_file.bak` **before** building
1. Build executable
1. Rename `settings_file.bak` to `settings_file.py`
1. Copy `settings_file.py` to `build/exe.(platform)-(python_version)/settings_file.py`

Otherwise it will build executable with settings_file.py as constant


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

    Empty page delimiter (Varies depending on site)
    > RegExp matching page with no images
    >> empty_page = "\[\]$"
    >> empty_page = "{images:\[\]"

    Additional params
    > Such as api keys
    >> params = '&key={}&username={}'.format(apikey, username)

    Parser Configuration
    > No time to explain


## Commands and Web-endpoints

### CLI

#### Main menu
Enter this commands if prompt starts with `DB>`

| Command            | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| help               | Shows in-app help                                                                       |
| get images         | Downloads images that you liked/favorited on *booru                                     |
| get images -f      | Same as get images --fast                                                                |
| get images --force | Downloads images without checking file existance                                        |
| get images --fast  | Checks for new images and downloads them using follower's settings                      |
| total              | Prints amount of entries in local DB                                                    |
| count \<tag\>      | Prints amount of entries tagged with \<tag\>                                            |
| show \<image_id>   | Opens image in image viewer or browser if no viewers found                              |
| quit (exit)        | Closes app                                                                              |
| \<anything>        | Uses input as list of tags and searches for it                                          |

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

| Endpoint               | Method | Parameters (Body for POST)          | Description                              | Returns                                                   |
| :--------------------: | :----: | ----------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| "/"                    | GET    |                                     | Main page                                | HTML-page                                                 |
| "/"                    | GET    | query=**search_query** page=**int** | Search images                            | HTML-page and HTTP headers and status code                |
| "/export"              | GET    | id=**filename**                     | Exports image to <export_path>           | Plain text data ("Done") and HTTP headers and status code |
| "/images/**filename**" | GET    |                                     | Access image file                        | Image and/or HTTP headers and status code                 |
| "/image/**str**"       | GET    |                                     | View image with tags                     | HTML-page and HTTP headers and status code                |
| "/dl"                  | GET    | id=**filename**                     | Browser-friendly download method         | Image and HTTP headers and status code                    |
| "/raw"                 | GET    | id=**filename**                     | Raw image data                           | Image without HTTP headers/status codes                   |
| "/panic"               | GET    |                                     | Shuts down WebUI server                  | Plain text data ("Done") and HTTP headers and status code |
| "/shutdown"            | GET    |                                     | Shuts down WebUI server                  | Plain text data ("Done") and HTTP headers and status code |
| "/predict"             | GET    | phrase=**search_query**             | Tries to predict search query            | Plain text data and HTTP headers and status code          |
| "/next"                | POST   | **int**                             | Tries to get id of next (older) image    | Plain text data (<id-of-image>) and status code           |
| "/previous"            | POST   | **int**                             | Tries to get id of previous(newer) image | Plain text data (<id-of-image>) and status code           |
| "/thumb/**filename**   | GET    |                                     | Makes thumbnail (500px) of image         | Image


## Search basics and syntax

### Basic search rules

1. Tags must be separated by **`,`** (comma)
>Example: "safe`,` princess luna"
2. Tags are not case sensitive
>Example: "SaFe" == "SafE" == "safe"
3. Search for "tag" will only return images tagged with "tag" not "tag*"
>Example: "safe" returns images with tag "safe" and doesn't returns "safezone"
4. Searching multiple tags will return images matching all the tags
>Example: "safe, princess luna" will return images tagged with both "safe" and "princess luna"
5. Exclude tags by placing **`-`** (hyphen-minus) before tag
>Example: "-safe" will return all images not tagged with "safe"
6. Rules 2,3,4 works almost the same for exclude

### Special tags

>Works only for filtering searches
>Example: width=100 (Works) while -width=100 (Doesn't works)

>Tip: `ratio` contains 10 symbols maximum

1. `height`
1. `width`
1. `ratio` or `aspect_ratio`

#### Syntax

1. **`=`** or **`==`** means equal to \<value>
1. **`!=`** or **`<>`** means not equal to \<value>
1. **`>`** means bigger than \<value>
1. **`<`** means less than \<value>
1. **`>=`** or **`=>`** means bigger or equal to \<value>
1. **`<=`** or **`=<`** means less or equal to \<value>
>Example: 'safe, width>100" will return images tagged with 'safe' tag and image width bigger than 100px


## Settings_file.py

| Option                | Format                        | Description                                              |
| --------------------- | ----------------------------- | -------------------------------------------------------- |
| modules               | List (['String', 'String'])    | Enables modules
| suppress_errors       | Bool (True/False)             | Prints errors and stacktrace in case of happening        |
| ssl_verify            | Bool (True/False) or String ("Path") | Enable/Disable ssl verification or set custom CA Cert |
| enable_proxy          | Bool (True/False)             | Enables/Disables proxy for requests    |
| socks5_proxy_ip       | String ("IP")                 | Sets proxy IP                                            |
| socks5_proxy_port     | String ("Port")               | Sets proxy port                                          |
| web_ip                | String ("IP")                 | Set IP to bind Web interface                             |
| web_port              | Integer (port)                | Sets port to bind Web interface                          |
| tag_amount            | Integer (number)              | Maximum tags per image                                   |
| showing_imgs          | Integer (number)              | How many images to show per page                         |
| showing_tags          | Integer (number)              | How many tags to **show** per image (CLI-only)           |
| images_path           | String ("Path")               | Where to store loaded images                             |
| export_path           | String ("Path")               | Where to store exported images                           |
| time_wait             | Integer (seconds)             | How long thread can stay alive                           |
| ids_file              | String ("Path/Filename")      | Name for tempfile (No need to change)                    |
| db_name               | String ("Path/Filename")      | Where to store DB file                                   |
| table_name            | String ("Text")               | Sets name for main table (No need to change)             |
| run_follower          | Bool (True/False)             | Enable checking for new images while webUI runs          |
| checked_pages         | Integer (number)              | How many pages should be checked                         |
| follower_sleep        | Integer (seconds)             | Defines time between checking for images                 |
| thread_cap            | Integer (number)              | Defines maximum running threads before blocking creating new threads |
| sleep_time            | integer (seconds)             | Defines time to wait before creating new thread after thread cap is reached |


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


## dermod/follow.py

Checks first pages of *booru api and downloads liked/faved images

>Due to `follow.py` implementation it won't download images that was uploaded long ago and liked now  
In that case you should use "`get images`" command of [CLI-version](#cli-version)
