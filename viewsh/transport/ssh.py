from viewsh import transport
from viewsh import stream
from viewsh.tools import log, shell_quote, list_to_command

import paramiko
import os
import subprocess

class SSHTransport(transport.CommandBasedTransport):
    def __init__(self, sock, username, parent):
        super(SSHTransport, self).__init__()
        self.transport = paramiko.Transport(sock)
        self.parent = parent
        self.transport.start_client()
        self._auth(self.transport, username)

    def execute(self, args, size=None, pty=False, cwd='/', environ={}):
        chan = self.transport.open_session()
        if pty:
            chan.get_pty('xterm', size[0], size[1])
        bufsize = 1 # ?
        stdin = chan.makefile('rb', bufsize)
        stdout = chan.makefile('wb', bufsize)
        # TODO: stderr?
        return stream.FileStream(stdin, stdout)

    def execute_get_output(self, args, cwd='/'):
        chan = self.transport.open_session()
        chan.exec_command(list_to_command(args))
        input = chan.makefile('rb')
        data = input.read()
        code = chan.recv_exit_status()
        if code != 0:
            raise subprocess.CalledProcessError(code, args)
        return data

    def real_path(self, path, need_dir):
        return self.execute_get_output(['realpath', shell_quote(path)]).strip()

    def _auth(self, transport, username):
        # TODO: known hosts
        # paramiko.RSAKey.from_private_key_file(key_path)

        agent = paramiko.Agent()
        agent_keys = agent.get_keys()

        for key in agent_keys:
            try:
                transport.auth_publickey(username, key)
                return
            except paramiko.SSHException:
                pass
