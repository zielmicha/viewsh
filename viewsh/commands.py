from viewsh.transport import ssh
from viewsh.transport import Transport
from viewsh.executor import Executor

def vssh(state, terminal, userhost):
    user, host = userhost.split('@')
    transport = ssh.SSHTransport(host, user, parent=state[Transport])
    state[Transport] = transport # TODO: .switch_transport

def register(state):
    state[Executor].commands['vssh'] = vssh
