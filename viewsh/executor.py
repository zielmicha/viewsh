from viewsh import task
from viewsh import stream
from viewsh import terminal

import shlex

class Executor(object):
    def __init__(self, state, terminal):
        self.state = state
        self.terminal = terminal

    def execute(self, command):
        if command == 'exit':
            raise SystemExit
        args = shlex.split(command)
        execution = self.state.transport.execute(args, size=self.terminal.get_size(),
                                           pty=True)
        q = task.Queue()
        execution.read_event = q
        execution.start()
        self.terminal.key_event = q
        for event in q:
            if isinstance(event, stream.StreamCloseEvent):
                break
            elif isinstance(event, stream.StreamReadEvent):
                self.terminal.write(event.data)
            elif isinstance(event, terminal.KeyEvent):
                execution.write(event.char)
