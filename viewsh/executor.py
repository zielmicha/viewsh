from viewsh import task
from viewsh import stream

import shlex

class Executor(object):
    def __init__(self, state, terminal, transport):
        self.state = state
        self.terminal = terminal
        self.transport = transport

    def execute(self, command):
        if command == 'exit':
            raise SystemExit
        args = shlex.split(command)
        execution = self.transport.execute(args)
        q = task.Queue()
        execution.read_event = q
        execution.start()
        for event in q:
            if isinstance(event, stream.StreamCloseEvent):
                break
            elif isinstance(event, stream.StreamReadEvent):
                self.terminal.write(event.data)
