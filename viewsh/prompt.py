from viewsh import rc
from viewsh.tools import log

PS1 = '{path} $ '

class Prompt(object):
    def __init__(self, state, terminal):
        self.terminal = terminal
        self.state = state

    def show(self):
        ps1 = getattr(self.state, 'ps1', PS1)
        prompt_text = rc.format_with_default_params(ps1, path=self.state.current_directory)
        self.terminal.write(prompt_text)
