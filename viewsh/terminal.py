from viewsh import task
import sys
import codecs

class Terminal(task.Task):
    def __init__(self):
        Task.__init__(self)
        self.key_event = task.NullQueue()

    def run(self):
        input = sys.stdin
        decoder = codecs.getincrementaldecoder('utf-8')
        while True:
            raw = input.read(1)
            chars = decoder.decode(raw)
            for ch in chars:
                self._feed(ch)

    def _feed(self, ch):
        pass

    def write(self, data):
        with self.lock:
            sys.stdout.write(data)

class KeyEvent(object):
    pass
