from viewsh.ui import toolkit
import pty

class Interface(object):
    def __init__(self):
        self.widget = toolkit.MultiWindow()
        self.last_windowid = 0
        self.buffers = []

    def create_default_layout(self, term):
        self.set_layout(0)
        self.set_window(0, term)

    def set_layout(self, layout):
        self.layout = layout
        self.widget.set_layout(layout)

    def _make_windowid(self):
        self.last_windowid += 1
        return self.last_windowid

    def make_sure_there_is_a_split(self):
        if isinstance(self.layout, int):
            self.set_layout(('hsplit',
                             self.layout, self._make_windowid()))

    def set_window(self, window_id, buffer):
        assert isinstance(buffer, Buffer), buffer
        assert buffer in self.buffers
        buffer.window_id = window_id
        self.widget.set_window(window_id, buffer.widget)

    def create_buffer(self, widget=None):
        buff = Buffer(iface=self)
        self.buffers.append(buff)
        buff.widget = widget
        return buff

    def create_terminal_buffer(self, **kwargs):
        term = toolkit.Terminal(**kwargs)
        buffer = self.create_buffer(term)
        master, slave = pty.openpty()
        term.set_pty(master)
        return slave, buffer

class Buffer(object):
    def __init__(self, iface, window_id=0):
        self.iface = iface
        self.window_id = window_id

    def set_nextto(self, widget):
        '''
        Chooses suitable window and replaces it with widget.
        Returns choosen window id.
        '''
        self.iface.make_sure_there_is_a_split()
        which = self.iface.layout[1]
        if which == self.window_id:
            which = self.iface.layout[2]
        self.iface.set_window(which, widget)
        return which

class InterfaceWrapper(object):
    def __init__(self, iface):
        self.iface = iface

    def __getattr__(self, name):
        orig = getattr(self.iface, name)
        def wrapper(*args, **kwargs):
            return toolkit.run_in_ui(lambda: orig(*args, **kwargs))

        return wrapper
