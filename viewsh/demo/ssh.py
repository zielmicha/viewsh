from viewsh import shell
from viewsh import terminal
from viewsh import rc
from viewsh import state
from viewsh import comm
from viewsh.transport import ssh, local
from viewsh.transport import Transport

terminal = terminal.Terminal()
terminal.start()
shell_state = state.ShellState()
shell_state[Transport] = ssh.SSHTransport(('users', 22), username='zlmch',
                                          parent=local.LocalTransport())
shell_state[comm.Interface].patch_log()
rc.setup(shell_state)
shell = shell.Shell(terminal, shell_state)
shell.loop()
