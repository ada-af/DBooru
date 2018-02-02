from threading import Thread
import time


class Error(Exception):
    pass


class Timeouted(Error):
    def __init__(self):
        pass


class Timer(Thread):
    def __init__(self, to):
        Thread.__init__(self)
        self.time = to
        self.done = 0

    def run(self):
        time.sleep(self.time)
        if self.done == 0:
            raise Timeouted

    def stop(self):
        self.done = 1


class ThreadController(Thread):
    @staticmethod
    def log_debug(*args):
        j = ''
        for i in args:
            j += str(i)
        print("[DEBUG] " + str(j))

    def __init__(self):
        Thread.__init__(self)
        self.threads = []

    def run(self):
        self.watcher()

    def watcher(self):
        while True:
            time.sleep(1)
            p = 0
            for i in self.threads:
                if i.readiness == 1:
                    self.threads.remove(i)
                    i.join()
                    del i
                    p = p + 1
