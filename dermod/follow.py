#!/usr/bin/env python3
import time
import settings_file
import sys
import os
import shutil
import importlib
from dermod import db, listloader, imgloader


def run(run_once=False):
    if settings_file.suppressor is True:
        silencer = open(os.devnull, 'w')
        sys.stderr = silencer
    while True:
        print("Checking new images")
        try:
            for i in settings_file.modules:
                module = importlib.import_module(
                    'dermod.sitesupport.{}'.format(i))
                listloader.run(
                    follower=True, pages_num=settings_file.checked_pages, module=module)
                imgloader.run(file=settings_file.ids_file, check_local=False)
                db.fill_db(file=settings_file.ids_file)
        except Exception as exc:
            print("Exception occured: "+exc.with_traceback(None))
        print("Cleanup")
        shutil.rmtree('tmp')
        os.remove(settings_file.ids_file)
        print("Done")
        if run_once is True:
            break
        time.sleep(settings_file.follower_sleep)
