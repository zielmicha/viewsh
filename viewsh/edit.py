from viewsh import termedit
from viewsh import task
from viewsh.tools import log, shell_quote
from viewsh.shell import History, CurrentDirectory
from viewsh.transport import Transport, FilterType

from functools import partial
import posixpath
import unittest

class LineEdit(termedit.TermLineEdit):
    def __init__(self, prompt, state, terminal):
        super(LineEdit, self).__init__(terminal)
        self.state = state
        self._prompt = prompt
        self.history_pos = len(self.state[History])
        self.completion_async = task.AsyncCall(self.q)
        self.key_history = []

    def handle_key(self, event):
        self.key_history.append(event.char)
        if event.type in ('up', 'down'):
            self.completion_async.abort()
            history = self.state[History]
            if not history: history = [self.buff]
            self.history_pos += +1 if event.type == 'down' else -1
            self.history_pos %= len(history)
            self.clear()
            self.add(history[self.history_pos])
        elif event.type == 'home':
            self.move_to(0)
        elif event.type == 'end':
            self.move_to(len(self.buff))
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
        self.state[History].append(self.buff)
        return super(LineEdit, self).finished()

    def complete(self):
        completor = self.state[Completor]
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

        self.completion_async.call(partial(completor.complete, self.buff[:pos]),
                        and_then=finish)

class Completor(object):
    pass_state = True

    def __init__(self, state):
        self.state = state

    def complete(self, buff):
        '''
        Perform completion. Returns tuple (possible completions, complete for sure).
        '''
        split = buff.split(' ')
        if not split:
            return buff
        if len(split) == 1:
            result = self.complete_command(split[0])
            return result, common_prefix_better_than(result, split[0])
        else:
            result = self.complete_option(split[0], split[-1])
            return result, ' '.join(split[:-1]) + ' ' + common_prefix_better_than(result, split[-1])

    def complete_option(self, cmd, option):
        filter_type = {'cd': FilterType.DIRECTORY}.get(cmd, FilterType.ANY)
        completions = self.state[Transport].file_completions(option,
                                                             cwd=self.state[CurrentDirectory],
                                                             filter_type=filter_type)
        return completions

    def complete_command(self, cmd):
        if cmd.startswith(('./', '/')):
            completions = self.state[Transport].\
                          file_completions(cmd,
                                           cwd=self.state[CurrentDirectory],
                                           filter_type=FilterType.EXECUTABLE)
            return completions
        else:
            return []

def common_prefix_better_than(arr, than):
    prefix = common_prefix(arr)
    if len(prefix) < len(than):
        return than
    else:
        return prefix

def common_prefix(arr):
    if not arr:
        return ''
    for i in xrange(max(map(len, arr))):
        prefix = arr[0][:i  ]
        if not all( item.startswith(prefix) for item in arr ):
            return prefix[:-1]
    return arr[0]

class CommonPrefixTest(unittest.TestCase):
    def test_common_prefix(self):
        assert common_prefix(['aaa', 'a']) == 'a'
        assert common_prefix([]) == ''
        assert common_prefix(['aaaa', 'b']) == ''
        assert common_prefix(['aaab', 'aab']) == 'aa'
