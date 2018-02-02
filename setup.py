import requests
from cx_Freeze import Executable, setup

buildOptions = {
    "packages": ["os", 'requests', 'queue', 'idna', 'gc', 'pysocks'],
    'includes': ['requests', 'dermod', 'queue', 'idna', 'gc', 'pysocks'],
    "excludes": ["tkinter"],
    'include_files': ["extra/", (requests.certs.where(), 'cacert.pem')]
}

setup(
    name="DBooru",
    version="1.0.0",
    requires=['requests', 'idna', 'gc', 'pysocks'],
    options={"build_exe": buildOptions},
    executables=[Executable("main.py"), Executable('webv3.py')]
)
