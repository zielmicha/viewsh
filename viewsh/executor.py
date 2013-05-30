from viewsh.tools import log
from viewsh import task
from viewsh import stream
from viewsh import terminal
from viewsh.state import CurrentDirectory
from viewsh.transport import Transport
from viewsh.comm import Interface

import shlex
import traceback
import sys
import posixpath

from functools import partial

class Executor(object):
    def __init__(self, state, terminal):
        self.state = state
        self.terminal = terminal

    def execute(self, command):
        proxy_term = terminal.ProxyTerminal(self.terminal)
        proxy_term.key_event = None
        q = task.Queue()
        self.terminal.key_event = q

        execution = Execution(self.state, proxy_term)
        def execute():
            execution.execute(command)
            q.stop()

        task.async(execute)

        for event in q:
            if proxy_term.key_event:
                # inferior is able to process ctrl-c itself
                proxy_term.key_event.post(event)
            else:
                if isinstance(event, terminal.KeyEvent) and event.char == '\x03':
                    break

        proxy_term.enabled = False

class Execution(object):
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
            self.call_command(self.execute_remote_command, args)

    def execute_remote_command(self, args):
        execution = self.state[Transport].execute(args, size=self.terminal.get_size(),
                                                  pty=True,
                                                  cwd=self.state[CurrentDirectory],
                                                  environ={'TERM': 'xterm'})
        q = task.Queue('execute_remote_command')
        execution.read_event = q
        execution.start()
        self.terminal.key_event = q
        self.terminal.check()
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
            self.terminal.write_normal('viewsh: %s\n' % err)
        except:
            traceback.print_exc()

    # chdir is in executor, because it may need to trigger user hooks
    def chdir(self, path):
        new_dir = posixpath.join(self.state[CurrentDirectory], path)
        self.state[CurrentDirectory] = self.state[Transport].real_path(new_dir)

    def command_exit(self):
        self.state[Interface].quit()

    def command_cd(self, dir):
        self.chdir(dir)
