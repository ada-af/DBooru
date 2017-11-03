# DBooru

- [DBooru](#dbooru)
    - [Features](#features)
        - [Both versions](#both-versions)
        - [CLI-version](#cli-version)
        - [Web-Interface](#web-interface)
    - [Installation](#installation)
        - [Dependencies](#dependencies)
        - [Configuration](#configuration)
        - [How to run](#how-to-run)
    - [Commands and Web-enpoints](#commands-and-web-enpoints)
        - [CLI](#cli)
            - [Main menu](#main-menu)
            - [Search](#search)
        - [Web](#web)
    - [Search basics and syntax](#search-basics-and-syntax)
        - [Basic search rules](#basic-search-rules)
        - [Special tags](#special-tags)
            - [Syntax](#syntax)

## Features
### Both versions
1. Search in downloaded images
    1. By tags
    1. By image dimensions
1. Viewing images
1. Multithreading
### CLI-version
1. Loading images from Derpibooru
    1. Even with proxy (socks5 only)
1. Discovering of databases in case of using in LAN (Turnable option)
### Web-Interface
1. Downloading images
1. Exporting images
1. Sharing images for LAN-clients (Turnable option)


## Installation
### Dependencies
>- Python 3.6+
>- pip
>- requests
>- requests[security]
>- pysocks
>- idna
>- cryptography
>- netifaces
>
>If you have PyOpenSSL installed - remove it
>
>Or you can launch extra/linux\_deps.sh or extra/windows\_deps.bat and wait for magic
    
You can download frozen package [here](https://bitbucket.org/anon_a/dbooru/downloads/) (64-bit linux only)
+ No need to install dependencies and/or python
+ Needs configuration anyway

### Configuration
1. [Get derpibooru Api Key](https://derpibooru.org/users/edit)
1. Replace "KEY GOES HERE" on line 10 in `settings_file.py` with your key
1. (Optionally) Change other settings

### How to run
1. Run `python main.py` (or `./main` in case of frozen package)
1. Type in "get images"
1. Wait
1. Search or run `python webv3.py` (or `./webv3` in case of frozen package)
1. ???
1. PROFIT

## Commands and Web-enpoints

### CLI

#### Main menu
Enter this commands if prompt starts with `DB>`

| Command            | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| help               | Shows in-app help                                                                       |
| get images         | Downloads images that you liked/favorited on Derpibooru                                 |
| get images -f      | Downloads images without checking file existance that you liked/favorited on Derpibooru |
| get images --force | Same as get images -f                                                                   |
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

| Endpoint               | Method | Parameters                          | Description                      | Returns                                                   |
| ---------------------- | ------ | ----------------------------------- | -------------------------------- | --------------------------------------------------------- |
| "/"                    | GET    |                                     | Main page                        | HTML-page                                                 |
| "/"                    | GET    | query=**search_query** page=**int** | Search images                    | HTML-page and HTTP headers and status code                |
| "/export"              | GET    | id=**filename**                     | Exports image to <export_path>   | Plain text data ("Done") and HTTP headers and status code |
| "/images/**filename**" | GET    |                                     | Access image file                | Image and/or HTTP headers and status code                 |
| "/image/**int**"       | GET    |                                     | View image with tags             | HTML-page and HTTP headers and status code                |
| "/dl"                  | GET    | id=**filename**                     | Browser-friendly download method | Image and HTTP headers and status code                    |
| "/raw"                 | GET    | id=**filename**                     | Raw image data                   | Image without HTTP headers/status codes                   |
| "/panic"               | GET    |                                     | Shuts down WebUI server          | Plain text data ("Done") and HTTP headers and status code |
| "/shutdown"            | GET    |                                     | Shuts down WebUI server          | Plain text data ("Done") and HTTP headers and status code |


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

>These tags support **`*`** (asterisk)
>Example: "safe, ratio=1.2*" will return images tagged 'safe' and image aspect ratio 1.20 or 1.23 or 1.288889 etc.

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
