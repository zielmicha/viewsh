from viewsh import prompt
from viewsh import edit
from viewsh import task
#from viewsh import executor

class Shell(object):
    Prompt = prompt.Prompt
    LineEdit = edit.LineEdit
    #Executor = executor.Executor

    def __init__(self, terminal, transport):
        self.terminal = terminal
        self.transport = transport
        self.prompt = self.Prompt(terminal, transport)
        #self.executor = self.Executor(terminal, transport)

    def single(self):
        self.prompt.show()
        line_edit = self.LineEdit(self.terminal, self.transport)
        line = line_edit.prompt()
        print 'executing', line
        if line == 'exit': raise SystemExit
        #self.executor.execute(line)

    def loop(self):
        while True:
            self.single()

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
