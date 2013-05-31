from viewsh.transport import ssh
from viewsh.transport import Transport
from viewsh.shell import SwitchTransport
from viewsh.executor import Executor

def vssh(state, terminal, userhost):
    user, host = userhost.split('@')
    transport = ssh.SSHTransport(host, user, parent=state[Transport])
    state[SwitchTransport].switch(transport)

def register(state):
    state[Executor].commands['vssh'] = vssh
