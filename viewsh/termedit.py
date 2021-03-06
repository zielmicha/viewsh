'''
Low level class implementing line edit in raw mode.
'''
from viewsh import task
from viewsh.tools import log
from viewsh.terminal import KeyEvent

from viewsh.letterutils import next_word, prev_word

class TermLineEdit(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self.buff = ''
        self.pos = 0
        self.q = task.Queue('termedit')
        self.__finished = False
        self.__termwrite = TerminalWriter(terminal)

    def reset_offset(self):
        self.screen_offset = self.terminal.get_cursor_position()[0] - 1

    def prompt(self):
        self.start_line()
        self.terminal.key_event = self.q
        for event in self.q:
            self.handle_event(event)
            if self.__finished:
                self.finish_line()
                return self.finished()

    def finish_line(self):
        self.move_to(len(self.buff))
        self.terminal.write('\r\n')

    def start_line(self):
        self.reset_offset()
        self.__termwrite.invalidate()
        self.__restore_after_line_cleared()

    def __restore_after_line_cleared(self):
        old_buff = self.buff
        old_pos = self.pos
        self.pos = 0
        self.buff = ''
        self.add(old_buff)
        self.move_to(old_pos)

    def finished(self):
        return self.buff

    def handle_event(self, event):
        if isinstance(event, KeyEvent):
            self.handle_key(event)

    def handle_key(self, event):
        if event.char in '\r\n':
            self.__finished = True
        elif event.char == '\x7f': # backspace
            self.backspace()
        elif event.char == '\x03': # ctrl-c
            self.clear()
        elif event.type == 'left':
            self.move(-1)
        elif event.type == 'right':
            self.move(+1)
        elif event.type == 'home':
            self.move_to(0)
        elif event.type == 'end':
            self.move_to(len(self.buff))
        elif event.type == 'c_right':
            self.move_to(next_word(self.buff, self.pos))
        elif event.type == 'c_left':
            self.move_to(prev_word(self.buff, self.pos))
        elif event.type == 'kill':
            self.kill()
        elif event.type == 'unknown_escape':
            pass
        elif len(event.char) == 1 and ord(event.char) >= 0x20:
            self.add(event.char)
        self.__normalize()

    def backspace(self):
        if self.pos > 0:
            self.buff = self.buff[:self.pos-1] + self.buff[self.pos:]
            self.__termwrite.backspace()
            self.pos -= 1
            self.__termwrite.clear_forward(len(self.buff) - self.pos + 1)
            self.add('') # reformat lines on the right

    def move(self, i):
        old = self.pos
        self.pos += i
        self.__normalize()
        new = self.pos
        self.pos = old
        while self.pos > new:
            self.__termwrite.move_back()
            self.pos -= 1
        while self.pos < new:
            self.__termwrite.move_forward()
            self.pos += 1

    def move_to(self, pos):
        self.move(pos - self.pos)

    def kill(self):
        self.__termwrite.clear_forward(len(self.buff) - self.pos)
        self.buff = self.buff[:self.pos]

    def clear(self):
        self.move_to(0)
        self.kill()

    def __normalize(self):
        self.pos = max(self.pos, 0)
        self.pos = min(self.pos, len(self.buff))

    def set(self, data):
        if data == self.buff: return
        self.clear()
        self.add(data)

    def add(self, data):
        ' Add data to buffer at current pos, and move cursor at the end of it.'
        self.__termwrite.start_buffering()
        end = self.buff[self.pos:]
        self.buff = self.buff[:self.pos] + data + self.buff[self.pos:]
        self.pos += len(data)
        self.__termwrite.add(data + end)
        for i in xrange(len(end)):
            self.__termwrite.move_back()
        self.__termwrite.end_buffering()

class TerminalWriter(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self.size = None
        self.cursor_position = None
        self.buffer = None

    def terminal_write(self, data):
        if self.buffer is not None:
            self.buffer.append(data)
        else:
            self.terminal.write(data)

    def start_buffering(self):
        self.buffer = []

    def end_buffering(self):
        self.terminal.write(''.join(self.buffer))
        self.buffer = None

    def get_size(self):
        if not self.size:
            self.size = self.terminal.get_size()
        return self.size

    def get_cursor_position(self):
        if not self.cursor_position:
            self.cursor_position = list(self.terminal.get_cursor_position())
        return self.cursor_position

    def backspace(self):
        self.move_back()
        pos = self.get_cursor_position()
        self.terminal_write(' ')
        self.set_cursor_pos(pos)

    def move_back(self):
        x, y = self.get_cursor_position()
        w, h = self.get_size()
        if x == 1:
            self.terminal_write('\x1b[A') # one line up
            self.terminal_write('\x1b[%dG' % (w - 1)) # to the end of line
            x, y = self.get_cursor_position()
            self.cursor_position = [w - 1, y - 1]
        else:
            self.terminal_write('\b')
            self.cursor_position[0] -= 1

    def move_forward(self):
        x, y = self.get_cursor_position()
        w, h = self.get_size()
        if x == w - 1:
            self.terminal_write('\x1b[B') # one line up
            self.terminal_write('\x1b[1G') # to the start of line
            x, y = self.get_cursor_position()
            self.cursor_position = [1, y + 1]
        else:
            self.terminal_write('\x1b[C')
            self.cursor_position[0] += 1

    def clear_forward(self, n):
        ' Clear next n characters '
        for i in xrange(n):
            self.move_forward()
        for i in xrange(n):
            self.backspace()

    def add(self, data):
        ' Add data at current position, assuming it is end. '
        w, h = self.terminal.get_size()
        lines_written = 0
        while data:
            x, y = self.get_cursor_position()
            space_left = w - x
            written_data = data[:space_left]
            self.terminal_write(written_data)
            lines_written += 1
            data = data[space_left:]
            if data:
                if y == h: # no more horizontal space
                    self.terminal_write('\x1b[1S')
                    self.set_cursor_pos((1, h))
                else:
                    self.set_cursor_pos((1, y + 1))
            else:
                self.cursor_position = [x + len(written_data), y]
        # not sure what terminal emulator will do - this may be necessary
        # if self.get_cursor_position()[0] >= w - 2:
        #     self.invalidate()

    def invalidate(self):
        self.cursor_position = None
        if self.buffer is not None:
            self.end_buffering()
            self.start_buffering()

    def set_cursor_pos(self, (x, y)):
        self.terminal_write('\x1b[%d;%dH' % (y, x))
        self.cursor_position = [x, y]
