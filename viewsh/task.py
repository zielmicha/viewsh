from Queue import Queue as _Queue
import threading

class Queue(object):
    def __init__(self):
        self._q = _Queue(0)

    def post(self, item):
        self._q.put(item)

    def __iter__(self):
        while True:
            yield self._q.get()

class NullQueue(object):
    def post(self, item):
        pass

class Task(object):
    def __init__(self):
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

    def __run(self):
        try:
            self.run()
        except:
            # normally, there is no sense to continue
            traceback.print_exc()
            os._exit(1)