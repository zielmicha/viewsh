from viewsh import termedit
from viewsh import task
from viewsh.tools import log

from functools import partial

class LineEdit(termedit.TermLineEdit):
    def __init__(self, prompt, terminal):
        super(LineEdit, self).__init__(terminal)
        self._prompt = prompt
        self.history_pos = len(self.get_history())
        self.completion_async = task.AsyncCall(self.q)
        self.key_history = []
        self.__default_history = []

    def handle_key(self, event):
        self.key_history.append(event.char)
        if event.type in ('up', 'down'):
            self.completion_async.abort()
            history = self.get_history()
            if not history: history = [self.buff]
            self.history_pos += +1 if event.type == 'down' else -1
            self.history_pos %= len(history)
            self.clear()
            self.add(history[self.history_pos])
        elif event.char == '\t':
            self.complete()
        elif event.char == '\x04':
            if not self.buff:
                self.add('exit')
        else:
            self.completion_async.abort()
            super(LineEdit, self).handle_key(event)

    def start_line(self):
        self._prompt.show()
        super(LineEdit, self).start_line()

    def finished(self):
        if self.buff.strip():
            self.save_history(self.buff)
        return super(LineEdit, self).finished()

    def save_history(self, line):
        self.__default_history.append(line)

    def get_history(self):
        return self.__default_history

    def invoke_complete(self, value):
        return [], value

    def complete(self):
        pos = self.pos

        def finish((results, prefix)):
            log("competion request ->", results, prefix, level=1)
            if len(results) > 1:
                if self.key_history[-2:] == ['\t', '\t']:
                    self.finish_line()
                    self.terminal.write_normal('\n'.join(results) + '\n')
                    self.start_line()
            self.set(prefix + self.buff[pos:])
            self.move_to(len(prefix))

        self.completion_async.call(partial(self.invoke_complete, self.buff[:pos]),
                        and_then=finish)
