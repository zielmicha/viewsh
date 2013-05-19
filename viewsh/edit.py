from viewsh import task
from viewsh.terminal import KeyEvent

class LineEdit(object):
    def __init__(self, terminal, transport):
        self.terminal = terminal
        self.transport = transport
        self.buff = ''
        self.finish = False

    def prompt(self):
        q = task.Queue()
        self.terminal.key_event = q
        for event in q:
            if isinstance(event, KeyEvent):
                self._handle_key(event)
            if self.finish:
                return self.buff

    def _handle_key(self, event):
        if event.char == '\n':
            self.finish = True
            self.terminal.write('\n')
        elif event.char:
            self.buff += event.char
            self.terminal.write(event.char)
