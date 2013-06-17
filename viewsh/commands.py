from viewsh.transport import ssh
from viewsh.transport import Transport
from viewsh.shell import SwitchTransport, CurrentDirectory, EnvCache
from viewsh.executor import Executor
from viewsh.ui.interface import Interface, Buffer
from viewsh.comm import World

import posixpath

def vssh(state, terminal, userhost):
    user, host = userhost.split('@')
    transport = ssh.SSHTransport(host, user, parent=state[Transport])
    state[SwitchTransport].switch(transport)

def nextto(state, terminal):
    ''' Open a shell next to the current. '''
    from viewsh.ui import main
    buffer = main.create_shell(world=state[World])

    state[Buffer].set_nextto(buffer)

def show(state, terminal, path):
    from viewsh.ui import toolkit
    abspath = posixpath.join(state[CurrentDirectory], path)
    data = state[Transport].get_file_content(abspath)
    widget = toolkit.Label(data)
    buffer = state[Interface].create_buffer(widget)

    state[Buffer].set_nextto(buffer)

def cd(state, terminal, dir=None):
    if not dir:
        dir = state[EnvCache].home
    state[Executor].chdir(dir)

def exit(state, terminal):
    if not state[SwitchTransport].empty():
        state[SwitchTransport].pop()
    else:
        raise SystemExit()

def register(state):
    state[Executor].commands['vssh'] = vssh
    state[Executor].commands['nextto'] = nextto
    state[Executor].commands['show'] = show
    state[Executor].commands['cd'] = cd
    state[Executor].commands['exit'] = exit
