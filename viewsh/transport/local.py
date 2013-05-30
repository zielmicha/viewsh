from viewsh.tools import log
from viewsh import transport
from viewsh import stream

import pty as _pty
import os
import fcntl
import termios
import struct
import signal
import traceback
import sys
import subprocess
import stat
import errno
import socket

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

class LocalTransport(transport.CommandBasedTransport):
    def __init__(self):
        super(LocalTransport, self).__init__()
        self.parent = None

    def execute(self, args, size=None, pty=False, cwd='/', environ={}):
        pid, fd = _pty.fork()
        if pid == 0:
            # child
            try:
                winsize = struct.pack("HHHH", size[1], size[0], 0, 0)
                fcntl.ioctl(0, termios.TIOCSWINSZ, winsize)
                os.environ.update(environ)
                os.chdir(cwd)
                os.system('stty iutf8')
                os.execvp(args[0], args)
            except (IOError, OSError) as err:
                sys.stderr.write('viewsh: %s: %s\n' % (args[0], err))
            except:
                traceback.print_exc()

            os._exit(0)
        else:
            fd2 = os.dup(fd)
            return stream.FileStream(os.fdopen(fd, 'r', 0), os.fdopen(fd2, 'w', 0))

    def execute_get_output(self, args, cwd='/'):
        return subprocess.check_output(args=args, cwd=cwd)

    def real_path(self, path, need_dir):
        new_path = os.path.realpath(path)
        s = os.stat(new_path)
        if need_dir:
            if not stat.S_ISDIR(s.st_mode):
                raise IOError(errno.ENOTDIR, 'Not a directory: %r' % new_path)
        return new_path

    def connect(self, host, port):
        sock = socket.socket()
        sock.connect((host, port))
        return sock
