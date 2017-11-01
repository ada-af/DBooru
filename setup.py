from cx_Freeze import setup, Executable
import requests

buildOptions = {"packages": ["os", 'requests', 'queue', 'idna'],
                'includes': ['requests', 'dermod', 'queue', 'idna'],
                "excludes": ["tkinter"],
                'include_files': ["extra/", (requests.certs.where(), 'cacert.pem')]
                }

setup(
    name="DBooru",
    version="1.0.0",
    requires=['requests', 'idna'],
    options={"build_exe": buildOptions},
    executables=[Executable("main.py"), Executable('webv3.py')]
)
