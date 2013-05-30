from viewsh import termedit
from viewsh import task
from viewsh.tools import log
from viewsh.state import History

from functools import partial

class LineEdit(termedit.TermLineEdit):
    def __init__(self, state, terminal):
        super(LineEdit, self).__init__(terminal)
        self.state = state
        self.history_pos = len(self.state[History])
        self.completion_async = task.AsyncCall(self.q)

    def handle_key(self, event):
        if event.type in ('up', 'down'):
            self.completion_async.abort()
            history = self.state[History]
            if not history: history = [self.buff]
            self.history_pos += +1 if event.type == 'down' else -1
            self.history_pos %= len(history)
            self.clear()
            self.add(history[self.history_pos])
        elif event.char == '\t':
            self.complete()
        else:
            self.completion_async.abort()
            return super(LineEdit, self).handle_key(event)

    def finished(self):
        self.state[History].append(self.buff)
        return super(LineEdit, self).finished()

    def complete(self):
        completor = self.state[Completor]
        pos = self.pos

        def finish(result):
            self.set(result + self.buff[pos:])
            self.move_to(len(result))

        self.completion_async.call(partial(completor.complete, self.buff[:pos]),
                        and_then=finish)

class Completor(object):
    def complete(self, buff):
        if buff == 'l':
            return 'ls '
        if buff == 'foo':
            import time
            time.sleep(1)
            return 'foobar '
        return buff
