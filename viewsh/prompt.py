
PS1 = '{path} $ '

class Prompt(object):
    def __init__(self, state, terminal):
        self.terminal = terminal
        self.state = state

    def show(self):
        self.terminal.write(PS1.format(path=self.state.current_directory))
