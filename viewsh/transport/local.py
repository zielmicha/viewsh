from viewsh import transport
from viewsh import stream

import pty
import os

class LocalTransport(transport.Transport):
    def __init__(self):
        super(LocalTransport, self).__init__()

    def execute(self, args):
        pid, fd = pty.fork()
        if pid == 0:
            # child
            os.execvp(args[0], args)
        else:
            return stream.FileStream(os.fdopen(fd, 'r', 0), os.fdopen(fd, 'w', 0))
