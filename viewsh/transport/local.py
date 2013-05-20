from viewsh import transport
from viewsh import stream

import pty as _pty
import os
import fcntl
import termios
import struct

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
            return stream.FileStream(os.fdopen(fd, 'r', 0), os.fdopen(fd, 'w', 0))
