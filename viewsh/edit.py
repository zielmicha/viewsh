from viewsh import task
from viewsh.terminal import KeyEvent

class LineEdit(object):
    def __init__(self, terminal, transport):
        self.terminal = terminal
        self.transport = transport
        self.buff = ''
        self.pos = 0
        self.finish = False
        self.termwrite = TerminalWriter(terminal)
        self._init()

    def _init(self):
        self.screen_offset = self.terminal.get_cursor_position()[0] - 1

    def prompt(self):
        q = task.Queue()
        self.terminal.key_event = q
        for event in q:
            if isinstance(event, KeyEvent):
                self._handle_key(event)
            if self.finish:
                return self.buff

    def _handle_key(self, event):
        if event.char == '\n':
            self.finish = True
            self.terminal.write('\n')
        elif event.char == '\x7f': # backspace
            if self.pos > 0:
                self.buff = self.buff[:self.pos-1] + self.buff[self.pos:]
                self.termwrite.backspace()
                self.pos -= 1
                self.termwrite.clear_forward(len(self.buff) - self.pos + 1)
                self.add('') # reformat lines on the right
        elif event.type == 'left':
            self.move(-1)
        elif event.type == 'right':
            self.move(+1)
        elif event.type == 'home':
            self.move_to(0)
        elif event.type == 'end':
            self.move_to(len(self.buff))
        elif event.type == 'kill':
            self.kill()
        elif event.char:
            self.add(event.char)
        self._normalize()

    def move(self, i):
        old = self.pos
        self.pos += i
        self._normalize()
        new = self.pos
        self.pos = old
        while self.pos > new:
            self.termwrite.move_back()
            self.pos -= 1
        while self.pos < new:
            self.termwrite.move_forward()
            self.pos += 1

    def move_to(self, pos):
        self.move(pos - self.pos)

    def kill(self):
        self.termwrite.clear_forward(len(self.buff) - self.pos)
        self.buff = self.buff[:self.pos]

    def _normalize(self):
        self.pos = max(self.pos, 0)
        self.pos = min(self.pos, len(self.buff))

    def add(self, data):
        ' Add data to buffer at current pos, and move cursor at the end of it.'
        end = self.buff[self.pos:]
        self.buff = self.buff[:self.pos] + data + self.buff[self.pos:]
        self.pos += len(data)
        self.termwrite.add(data + end)
        for i in xrange(len(end)):
            self.termwrite.move_back()

class TerminalWriter(object):
    def __init__(self, terminal):
        self.terminal = terminal

    def backspace(self):
        self.move_back()
        pos = self.terminal.get_cursor_position()
        self.terminal.write(' ')
        self.set_cursor_pos(pos)

    def remove_all(self):
        pass

    def move_back(self):
        x, y = self.terminal.get_cursor_position()
        w, h = self.terminal.get_size()
        if x == 1:
            self.terminal.write('\x1b[A') # one line up
            self.terminal.write('\x1b[%dG' % (w - 1)) # to the end of line
        else:
            self.terminal.write('\b')

    def move_forward(self):
        x, y = self.terminal.get_cursor_position()
        w, h = self.terminal.get_size()
        _debug(x, y, w, h)
        if x == w - 1:
            self.terminal.write('\x1b[B') # one line up
            self.terminal.write('\x1b[1G') # to the start of line
        else:
            self.terminal.write('\x1b[C')

    def clear_forward(self, n):
        ' Clear next n characters '
        for i in xrange(n):
            self.move_forward()
        for i in xrange(n):
            self.backspace()

    def add(self, data):
        ' Add data at current position, assuming it is end. '
        w, h = self.terminal.get_size()
        while data:
            x, y = self.terminal.get_cursor_position()
            space_left = w - x
            self.terminal.write(data[:space_left])
            data = data[space_left:]
            _debug(space_left, data)
            if data:
                if y == h: # no more horizontal space
                    self.terminal.write('\x1b[1S')
                    self.set_cursor_pos((1, h))
                else:
                    self.set_cursor_pos((1, y + 1))

        #if data[space_left:]:
        #    self.set_cursor_pos((w, h))
        #    #self.terminal.write(' ')
        #    self.terminal.write(data[space_left:])

    def set_cursor_pos(self, (x, y)):
        self.terminal.write('\x1b[%d;%dH' % (y, x))

def _debug(*args):
    if 1:
        print >>open('log', 'a'), args
