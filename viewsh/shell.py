from viewsh import prompt
from viewsh import edit
from viewsh import task
from viewsh import executor
from viewsh import comm

class Shell(object):
    Prompt = prompt.Prompt
    LineEdit = edit.LineEdit
    Executor = executor.Executor

    def __init__(self, terminal, transport):
        self.terminal = terminal
        self.transport = transport
        self.state = ShellState()
        self.prompt = self.Prompt(self.state, terminal, transport)
        self.executor = self.Executor(self.state, terminal, transport)

    def single(self):
        self.prompt.show()
        line_edit = self.LineEdit(self.state, self.terminal, self.transport)
        line = line_edit.prompt()
        self.executor.execute(line)

    def loop(self):
        while True:
            self.single()

class ShellState(object):
    def __init__(self):
        self.history = []
        self.interface = comm.Interface()
        self.interface.log('ShellState init')
        self.interface.patch_log()

def main():
    from viewsh.transport import local
    from viewsh import terminal
    terminal = terminal.Terminal()
    terminal.start()
    transport = local.LocalTransport()
    shell = Shell(terminal, transport)
    shell.loop()

if __name__ == '__main__':
    main()
