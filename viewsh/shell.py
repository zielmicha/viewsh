from viewsh.tools import log
from viewsh import prompt
from viewsh import edit
from viewsh import task
from viewsh import executor
from viewsh import state
from viewsh import comm
from viewsh.transport import Transport
from viewsh.transport import local

class Shell(object):
    Prompt = prompt.Prompt
    LineEdit = edit.LineEdit
    Executor = executor.Executor

    def __init__(self, terminal, state):
        self.terminal = terminal
        self.state = state
        self.prompt = self.Prompt(self.state, terminal)

        # this is circular dependency - this is bad
        self.state[executor.Executor] = self.Executor(self.state, terminal)

    def single(self):
        self.prompt.show()
        line_edit = self.LineEdit(self.state, self.terminal)
        line = line_edit.prompt()
        self.state[executor.Executor].execute(line)

    def loop(self):
        while True:
            self.single()

def main():
    from viewsh import terminal
    from viewsh import rc
    terminal = terminal.Terminal()
    terminal.start()
    shell_state = state.ShellState()
    shell_state[Transport] = local.LocalTransport()
    shell_state[comm.Interface].patch_log()
    rc.setup(shell_state)
    shell = Shell(terminal, shell_state)
    shell.loop()

if __name__ == '__main__':
    main()
