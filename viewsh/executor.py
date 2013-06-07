from viewsh.tools import log, shell_quote
from viewsh import task
from viewsh import stream
from viewsh import terminal
from viewsh.shell import CurrentDirectory, SwitchTransport, \
    EnvCache
from viewsh.transport import Transport
from viewsh.comm import Interface

import shlex
import traceback
import sys
import posixpath

from functools import partial

class Executor(object):
    pass_state = True

    def __init__(self, state):
        self.state = state
        self.aliases = {}
        self.commands = {}

    def resolve_alias(self, name):
        return self.aliases.get(name, shell_quote(name))

    def execute(self, term, command):
        proxy_term = terminal.ProxyTerminal(term)
        proxy_term.key_event = None
        q = task.Queue()
        term.key_event = q

        execution = Execution(self, self.state, proxy_term)
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
            if isinstance(event, terminal.KeyEvent) and event.char == '\x1c':
                # always terminate
                break

        proxy_term.enabled = False

class Execution(object):
    def __init__(self, executor, state, terminal):
        self.state = state
        self.terminal = terminal
        self.executor = executor

    def execute(self, command):
        args = shlex.split(command)
        if not args:
            return
        resolved_alias = self.executor.resolve_alias(args[0])
        args[:1] = shlex.split(resolved_alias)
        func = self.executor.commands.get(args[0])
        if not func:
            func = getattr(self, 'command_' + args[0], None)
        else:
            func = partial(func, self.state, self.terminal)
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
        except SystemExit:
            raise
        except:
            traceback.print_exc()

    def chdir(self, path):
        new_dir = posixpath.join(self.state[CurrentDirectory], path)
        self.state[CurrentDirectory] = self.state[Transport].real_path(new_dir, need_dir=True)

    def command_exit(self):
        if not self.state[SwitchTransport].empty():
            self.state[SwitchTransport].pop()
        else:
            raise SystemExit()

    def command_cd(self, dir=None):
        if not dir:
            dir = self.state[EnvCache].home
        self.chdir(dir)
