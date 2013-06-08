from viewsh import edit
from viewsh.shell import History, CurrentDirectory
from viewsh.transport import Transport, FilterType
from viewsh.tools import shell_quote

import unittest

class ShellLineEdit(edit.LineEdit):
    def __init__(self, prompt, state, terminal):
        self.state = state
        super(ShellLineEdit, self).__init__(prompt, terminal)

    def save_history(self, line):
        self.state[History].append(line)

    def get_history(self):
        return self.state[History]

    def invoke_complete(self, value):
        return self.state[Completor].complete(value)

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
            return [ i + ' ' for i in completions ]
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
