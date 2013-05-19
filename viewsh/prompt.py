
class Prompt(object):
    def __init__(self, terminal, transport):
        self.terminal = terminal
        self.transport = transport

    def show(self):
        self.terminal.write('$ ')
