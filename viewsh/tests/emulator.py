from viewsh import termemu
from viewsh import task

import pty
import os
import time
import sys
import termios
import struct
import fcntl

class Emulator(object):
    def __init__(self, width=40):
        self.width = width
        self.term = termemu.Terminal(10, self.width)
        self.term.expanded_modes['7'] = True # autowrap
        self.spawn()

    def spawn(self):
        pid, fd = pty.fork()
        if pid == 0:
            self._child()
        else:
            winsize = struct.pack("HHHH", 10, self.width, 0, 0)
            fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
            self.master = fd
            self.term.callbacks[termemu.CALLBACK_DSR]['emu'] = self.type
            task.async(lambda: _copy(fd, self.term))

    def type(self, text):
        os.write(self.master, text)

    def show(self):
        print '-' * (self.width + 2)
        for line in self.term.dump():
            print '|%s|' % ''.join(line)
        print '-' * (self.width + 2)

    def _child(self):
        from viewsh.main import UINotAvailable
        from viewsh import rc
        from viewsh import comm
        from viewsh.ui.interface import Interface
        world = comm.World()
        world[Interface] = UINotAvailable()
        rc.main(0, world, UINotAvailable(), setup_func=self._child_setup)

    def _child_setup(self, state):
        pass

    def _matches_p(self, lines):
        for line, real_line in zip(lines, self.term.dump()):
            if line.strip() != real_line.strip():
                return False
        return True

    def expect(self, *lines):
        for i in xrange(15):
            if self._matches_p(lines):
                return
            time.sleep(0.04)
        print 'lines:'
        for line in lines:
            print '    "%s"' % line
        print 'not matched'
        self.show()
        sys.exit(1)

class FakeTransport(object):
    pass

def _copy(fd, term):
    try:
        while True:
            data = os.read(fd, 1)
            term.write(data)
    except OSError as err:
        print err
