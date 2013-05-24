from viewsh.tools import log
from viewsh import task
from viewsh import stream
from viewsh import terminal

import shlex
import traceback
import sys

class Executor(object):
    def __init__(self, state, terminal):
        self.state = state
        self.terminal = terminal

    def execute(self, command):
        args = shlex.split(command)
        if not args:
            return
        func = getattr(self, 'command_' + args[0], None)
        if func:
            self.call_command(func, *args[1:])
        else:
            return self.call_command(self.execute_remote_command, args)

    def execute_remote_command(self, args):
        execution = self.state.transport.execute(args, size=self.terminal.get_size(),
                                                 pty=True,
                                                 cwd=self.state.current_directory,
                                                 environ={'TERM': 'xterm'})
        q = task.Queue('execute_remote_command')
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

    def call_command(self, func, *args):
        try:
            func(*args)
        except (IOError, OSError) as err:
            sys.stderr.write('viewsh: %s\n' % err)
        except:
            traceback.print_exc()

    def command_exit(self):
        raise SystemExit

    def command_cd(self, dir):
        self.state.chdir(dir)
