from viewsh import prompt
from viewsh import edit
from viewsh import task
from viewsh import executor
from viewsh import comm
from viewsh.transport import local

class Shell(object):
    Prompt = prompt.Prompt
    LineEdit = edit.LineEdit
    Executor = executor.Executor

    def __init__(self, terminal, state):
        self.terminal = terminal
        self.state = state
        self.prompt = self.Prompt(self.state, terminal)
        self.executor = self.Executor(self.state, terminal)

    def single(self):
        self.prompt.show()
        line_edit = self.LineEdit(self.state, self.terminal)
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
        self.transport = local.LocalTransport()

def main():
    from viewsh import terminal
    terminal = terminal.Terminal()
    terminal.start()
    state = ShellState()
    shell = Shell(terminal, state)
    shell.loop()

if __name__ == '__main__':
    main()
