from viewsh.transport import ssh
from viewsh.transport import Transport
from viewsh.shell import SwitchTransport, CurrentDirectory
from viewsh.executor import Executor
from viewsh.comm import Interface

import posixpath

def vssh(state, terminal, userhost):
    user, host = userhost.split('@')
    transport = ssh.SSHTransport(host, user, parent=state[Transport])
    state[SwitchTransport].switch(transport)

def nextto(state, terminal):
    ''' Open a shell next to the current. '''
    from viewsh.ui import main
    iface = state[Interface].create_child()
    term = main.create_shell(iface)

    iface.window_id = state[Interface].set_nextto(term)

def show(state, terminal, path):
    from viewsh.ui import toolkit
    abspath = posixpath.join(state[CurrentDirectory], path)
    data = state[Transport].get_file_content(abspath)
    widget = toolkit.Label(data)

    state[Interface].set_nextto(widget)

def register(state):
    state[Executor].commands['vssh'] = vssh
    state[Executor].commands['nextto'] = nextto
    state[Executor].commands['show'] = show
