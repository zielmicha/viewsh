from viewsh import transport
from viewsh import stream

import pty as _pty
import os
import fcntl
import termios
import struct
import signal

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

class LocalTransport(transport.Transport):
    def __init__(self):
        super(LocalTransport, self).__init__()

    def execute(self, args, size=None, pty=False):
        pid, fd = _pty.fork()
        if pid == 0:
            # child
            winsize = struct.pack("HHHH", size[1], size[0], 0, 0)
            fcntl.ioctl(0, termios.TIOCSWINSZ, winsize)
            os.system('stty iutf8')
            os.execvp(args[0], args)
        else:
            f = os.fdopen(fd, 'r+', 0)
            return stream.FileStream(f, f)
