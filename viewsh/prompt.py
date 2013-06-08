from viewsh.tools import log
from viewsh.shell import CurrentDirectory, format_with_default_params, \
    EnvCache
from viewsh.transport import Transport

class PS1(object):
    def __new__(cls):
        return '{path} $ '

class Prompt(object):
    def __init__(self, state, terminal):
        self.terminal = terminal
        self.state = state

    def show(self):
        log('rendering prompt', level=1)
        self.make_whole_line()
        ps1 = self.state[PS1]
        environ = self.state[EnvCache].environ
        prompt_text = format_with_default_params(ps1,
                                                 path=self.state[CurrentDirectory],
                                                 host=self.state[Transport].get_hostname(),
                                                 user=environ.get('USER'))
        self.terminal.write_normal(prompt_text)

    def make_whole_line(self):
        if self.terminal.get_cursor_position()[0] != 1:
            self.terminal.write_normal('\n')
