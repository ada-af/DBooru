## Installation ##
   ### Dependencies ###
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
    
You can download frozen package [here](https://bitbucket.org/anon_a/dbooru/downloads/DBooru(linux_x86_64).tar) (64-bit linux only)
+ No need to install dependencies and/or python
+ Needs configuration anyway

### Configuration ###
1. [Get derpibooru Api Key](https://derpibooru.org/users/edit)
1. Replace "KEY GOES HERE" on line 10 in `settings_file.py` with your key
1. (Optionally) Change other settings

### How to run ###
1. Run `python main.py` (or `./main` in case of frozen package)
1. Type in "get images"
1. Wait
1. Search or run `python webv3.py` (or `./webv3` in case of frozen package)
1. ???
1. PROFIT