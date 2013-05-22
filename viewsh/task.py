from Queue import Queue as _Queue
import threading
import traceback
import sys
import os

class Queue(object):
    def __init__(self):
        self._q = _Queue(0)
        self._senitel = object()
        self._stopped = False

    def post(self, item):
        self._q.put(item)

    def get(self):
        if self._stopped:
            raise StopIteration()
        value = self._q.get()
        if value is self._senitel:
            raise StopIteration()
        return value

    def stop(self):
        # works only if there is one thread waiting!
        self._stopped = True
        self._q.put(self._senitel)

    def __iter__(self):
        while True:
            yield self.get()

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
            # normally, there is no point to continue
            traceback.print_exc()
            sys.exitfunc()
            os._exit(1)
