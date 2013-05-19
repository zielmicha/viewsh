
class Prompt(object):
    def __init__(self, state, terminal, transport):
        self.terminal = terminal
        self.transport = transport
        self.state = state

    def show(self):
        self.terminal.write('$ ')
