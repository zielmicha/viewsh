from viewsh import termedit
from viewsh import task
from viewsh.tools import log, shell_quote
from viewsh.state import History, CurrentDirectory
from viewsh.transport import Transport

from functools import partial
import posixpath

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
    pass_state = True

    def __init__(self, state):
        self.state = state

    def complete(self, buff):
        split = buff.split(' ')
        if not split:
            return buff
        if len(split) == 1:
            return self.complete_command(split[0])
        else:
            result = self.complete_option(split[0], split[-1])
            return ' '.join(split[:-1]) + ' ' + result

    def complete_option(self, cmd, option):
        dirs_only = cmd == 'cd'
        completions = self.state[Transport].file_completions(option,
                                                             cwd=self.state[CurrentDirectory],
                                                             dirs_only=dirs_only)
        if len(completions) == 1:
            if dirs_only: completions[0] += '/'
            return shell_quote(completions[0])
        else:
            return option

    def complete_command(self, cmd):
        return cmd
