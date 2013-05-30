from viewsh import termedit
from viewsh.tools import log
from viewsh.state import History

class LineEdit(termedit.TermLineEdit):
    def __init__(self, state, terminal):
        super(LineEdit, self).__init__(terminal)
        self.state = state
        self.history_pos = len(self.state[History])

    def handle_key(self, event):
        if event.type in ('up', 'down'):
            history = self.state[History]
            if not history: history = [self.buff]
            self.history_pos += +1 if event.type == 'down' else -1
            self.history_pos %= len(history)
            self.clear()
            self.add(history[self.history_pos])
        else:
            return super(LineEdit, self).handle_key(event)

    def finished(self):
        self.state[History].append(self.buff)
        return super(LineEdit, self).finished()
