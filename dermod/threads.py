from threading import Thread
import time
import socket
import main
import settings_file


class BgTaskHost(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.port = 0
        
    def run(self):
        self.background_host()

    def background_host(self):
        import main
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', 0))
        self.port = sock.getsockname()[1]
        while True:
            data, addr = sock.recvfrom(4)
            if data == b"UPDT":
                print('GOT DATA')
                main.update_db()
                os.remove('update.lck')
        

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
