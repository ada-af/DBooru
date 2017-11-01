from cx_Freeze import setup, Executable
import requests
import sys

buildOptions = {"packages": ["os", 'requests', 'queue'],
                'includes': ['requests', 'dermod', 'queue'],
                "excludes": ["tkinter"],
                'include_files': ["extra/", (requests.certs.where(), 'cacert.pem')]
}

setup(
    name = "DBooru",
    version = "1.0.0",
    requires = 'requests',
    options = {"build_exe": buildOptions},
    executables = [Executable("main.py"), Executable('webv3.py')]
)
