from viewsh.tools import log
from viewsh.state import CurrentDirectory, format_with_default_params

class PS1(object):
    def __new__(cls):
        return '{path} $ '

class Prompt(object):
    def __init__(self, state, terminal):
        self.terminal = terminal
        self.state = state

    def show(self):
        ps1 = self.state[PS1]
        prompt_text = format_with_default_params(ps1, path=self.state[CurrentDirectory])
        self.terminal.write(prompt_text)
