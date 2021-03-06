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
        self._do_execute_command(chan, args, cwd)
        bufsize = 0
        stdin = NonBufferedSocketInput(chan)
        stdout = chan.makefile('wb', bufsize)
        # TODO: stderr?
        return stream.FileStream(stdin, stdout, buffer_size=1024)

    def execute_get_output(self, args, cwd='/'):
        chan = self.transport.open_session()
        self._do_execute_command(chan, args, cwd)
        input = chan.makefile('rb')
        data = input.read()
        code = chan.recv_exit_status()
        if code != 0:
            raise subprocess.CalledProcessError(code, args)
        return data

    def _do_execute_command(self, chan, args, cwd):
        prefix = 'cd %s' % shell_quote(cwd)
        chan.exec_command(prefix + ';' + list_to_command(args))

    def real_path(self, path, need_dir):
        return self.execute_get_output(['realpath', shell_quote(path)]).strip()

    def get_file_content(self, path):
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        f = sftp.open(path)
        try:
            data = f.read()
        finally:
            f.close()
        return data

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

class NonBufferedSocketInput(object):
    def __init__(self, sock):
        self.sock = sock

    def read(self, size):
        return self.sock.recv(size)
