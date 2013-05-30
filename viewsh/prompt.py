from viewsh.tools import log
from viewsh.state import CurrentDirectory, format_with_default_params
from viewsh.transport import Transport

class PS1(object):
    def __new__(cls):
        return '{path} $ '

class Prompt(object):
    def __init__(self, state, terminal):
        self.terminal = terminal
        self.state = state
        self._environ = None # cache

    def show(self):
        ps1 = self.state[PS1]
        if not self._environ:
            self._environ = self.state[Transport].get_environ()
        prompt_text = format_with_default_params(ps1,
                                                 path=self.state[CurrentDirectory],
                                                 host=self.state[Transport].get_hostname(),
                                                 user=self._environ.get('USER'))
        self.terminal.write(prompt_text)
