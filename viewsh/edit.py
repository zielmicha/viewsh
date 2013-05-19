from viewsh import termedit

class LineEdit(termedit.TermLineEdit):
    def __init__(self, state, terminal, transport):
        super(LineEdit, self).__init__(terminal)
        self.transport = transport
        self.state = state
        self.history_pos = len(self.state.history)

    def handle_key(self, event):
        if event.type in ('up', 'down'):
            history = self.state.history
            if not history: history = [self.buff]
            self.history_pos += +1 if event.type == 'down' else -1
            self.history_pos %= len(history)
            self.clear()
            self.add(history[self.history_pos])
        else:
            return super(LineEdit, self).handle_key(event)

    def finished(self):
        self.state.history.append(self.buff)
        return super(LineEdit, self).finished()
