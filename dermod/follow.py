#!/usr/bin/env python3
import time
import settings_file
import sys
import os
import shutil
from dermod import db, derpilist_v2, derpiload_v3


def run(run_once=False):
    if settings_file.suppressor is True:
        silencer = open(os.devnull, 'w')
        sys.stderr = silencer
    while True:
        print("Checking new images")
        derpilist_v2.run(follower=True, pages_num=settings_file.checked_pages)
        derpiload_v3.run(file=settings_file.ids_file, check_local=False)
        db.fill_db(file=settings_file.ids_file)
        print("Cleanup")
        shutil.rmtree('tmp')
        os.remove(settings_file.ids_file)
        print("Done")
        if run_once is True:
            break
        time.sleep(settings_file.follower_sleep)