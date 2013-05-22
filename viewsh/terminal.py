from viewsh import task
from viewsh.tools import log
import sys
import codecs
import tty, termios
import atexit
import os
import traceback
import fcntl
import termios
import struct

class Terminal(task.Task):
    '''
    Handles reading from and writing to terminal.
    '''
    def __init__(self):
        task.Task.__init__(self)
        self.key_event = task.NullQueue()
        self.get_cursor_position_event = task.Queue()
        self._buff = ''
        self.stdout = os.fdopen(1, 'w', 0)

    def run(self):
        self._init()
        try:
            self._run()
        finally:
            self._finish()

    def get_cursor_position(self):
        self.get_cursor_position_event = task.Queue()
        self.write('\x1b[6n')
        data = self.get_cursor_position_event.get()
        return map(int, data.split(';'))[::-1]

    def _init(self):
        self._termattrs = termios.tcgetattr(0)
        tty.setraw(0)
        atexit.register(self._finish, 0)
        sys.stdout = sys.stderr = NormalWriter(self)

    def _finish(self, *args):
        termios.tcsetattr(0, termios.TCSANOW, self._termattrs)

    def _run(self):
        input = os.fdopen(0, 'r', 0)
        decoder = codecs.getincrementaldecoder('utf-8')()
        while True:
            raw = input.read(1)
            chars = decoder.decode(raw)
            for ch in chars:
                self._feed(ch)

    def _feed(self, ch):
        ' Called when new character arrives '
        self._buff += ch
        try:
            self._consume(self._buff)
        except _NotReady:
            pass
        else:
            self._buff = ''

    def _consume(self, data):
        ''' Called with current buffer. If it doesn't constitute
        single keystroke raises _NotReady. '''
        if data[0] == '\x0b':
            self._post(KeyEvent('kill', char='\x0b'))
        elif data[0] == '\x1b' and data[1:2] in '[O':
            if len(data) <= 2 or data[-1] in '1234567890[;\x1b':
                raise _NotReady
            else:
                code = data[-1]
                self._handle_code(code, data[2:-1], data[1])
        else:
            self._post(KeyEvent(char=data[0]))

    def _post(self, ev):
        self.key_event.post(ev)

    def _handle_code(self, code, data, mode_ind):
        kind = {'A': const.up,
                'B': const.down,
                'C': const.right,
                'D': const.left,
                'F': const.end,
                'H': const.home,}.get(code)
        if kind:
            self._post(KeyEvent(kind, char='\x1b' + mode_ind + data + code))
        if code == 'R':
            self.get_cursor_position_event.post(data)

    def write(self, data):
        with self.lock:
            self.stdout.write(data)

    def write_normal(self, data):
        self.write(data.replace('\n', '\r\n'))

    def get_size(self):
        return struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, '1234'))[::-1]

    def get_width(self):
        return self.get_size()[0]

class NormalWriter(object):
    ''' Write to raw terminal as if it isn't raw. '''
    def __init__(self, terminal):
        self.terminal = terminal

    def write(self, data):
        self.terminal.write_normal(data)

    def flush(self):
        pass

class KeyEvent(object):
    def __init__(self, type='char', char=None):
        assert char
        self.char = char
        self.type = type

    def __repr__(self):
        return '<KeyEvent %s char=%r>' % (self.type, self.char)

class KeyConst:
    pass

const = KeyConst

for i in ['up', 'down', 'right', 'left', 'char', 'home', 'end', 'kill']:
    setattr(const, i, i)

class _NotReady(Exception):
    pass
