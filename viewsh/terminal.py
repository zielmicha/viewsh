from viewsh import task
from viewsh.tools import log, Exit
import sys
import codecs
import tty, termios
import atexit
import os
import traceback
import fcntl
import termios
import struct

class BaseTerminal(object):
    def write_normal(self, data):
        self.write(data.replace('\n', '\r\n'))

    def get_width(self):
        return self.get_size()[0]

class Terminal(task.Task, BaseTerminal):
    '''
    Handles reading from and writing to terminal.
    '''
    def __init__(self, tty):
        task.Task.__init__(self)
        self.key_event = task.NullQueue()
        self.get_cursor_position_event = task.Queue()
        self._buff = ''
        self._tty = tty
        self.stdout = os.fdopen(self._tty, 'w', 0)

    def run(self):
        self._init()
        try:
            self._run()
        except IOError as err:
            # when master tty is closed, errno 5 is raised
            log(err)
        finally:
            self._finish()

    def get_cursor_position(self):
        self.get_cursor_position_event = task.Queue()
        self.write('\x1b[6n')
        data = self.get_cursor_position_event.get()
        return map(int, data.split(';'))[::-1]

    def _init(self):
        self._termattrs = termios.tcgetattr(self._tty)
        tty.setraw(self._tty)
        atexit.register(self._finish)

    def _finish(self, *args):
        if self._tty == 0:
            termios.tcsetattr(self._tty, termios.TCSANOW, self._termattrs)
        # not needed if run in vte

    def _run(self):
        input = os.fdopen(self._tty, 'r', 0)
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
        log('KeyEvent', ev, '->', self.key_event, level=2)
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

    def get_size(self):
        return struct.unpack('hh', fcntl.ioctl(self._tty, termios.TIOCGWINSZ, '1234'))[::-1]

    def check(self):
        ''' check if terminal is still working '''
        pass

class ProxyTerminal(BaseTerminal):
    def __init__(self, terminal):
        self.terminal = terminal
        self.key_event = task.NullQueue()
        self.enabled = True

    def get_size(self):
        return self.terminal.get_size()

    def write(self, data):
        if self.enabled:
            self.terminal.write(data)

    def check(self):
        if not self.enabled:
            raise Exit()

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

class Color:
    seq = '\x1B[%sm'
    reset = seq % 0
    bold = seq % 1

def _setup():
    colors = ['grey',
               'red',
               'green',
               'yellow',
               'blue',
               'magenta',
               'cyan',
               'white']
    for i, name in enumerate(colors):
        setattr(Color, name, Color.seq % (i + 30))
        setattr(Color, 'on_%s' % name, Color.seq % (i + 40))

_setup()

class _NotReady(Exception):
    pass
