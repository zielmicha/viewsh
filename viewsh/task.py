from Queue import Queue as _Queue
import threading

class Queue(object):
    def __init__(self):
        self._q = _Queue(0)

class NullQueue(object):
    pass

class Task(object):
    def __init__(self):
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
