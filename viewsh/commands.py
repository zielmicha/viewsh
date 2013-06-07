from viewsh.transport import ssh
from viewsh.transport import Transport
from viewsh.shell import SwitchTransport
from viewsh.executor import Executor
from viewsh.comm import Interface

def vssh(state, terminal, userhost):
    user, host = userhost.split('@')
    transport = ssh.SSHTransport(host, user, parent=state[Transport])
    state[SwitchTransport].switch(transport)

def nextto(state, terminal):
    ''' Open a shell next to the current. '''
    from viewsh.ui.toolkit import Label
    state[Interface].set_nextto(Label('wtf'))

def register(state):
    state[Executor].commands['vssh'] = vssh
    state[Executor].commands['nextto'] = nextto
