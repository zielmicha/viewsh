from viewsh.ui import toolkit

class GlobalInterface(object):
    def __init__(self):
        self.widget = toolkit.MultiWindow()
        self.last_windowid = 0

    def create_default_shell(self, master_pty_fd):
        term = toolkit.Terminal()
        term.set_pty(master_pty_fd)
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

    def set_window(self, window_id, widget):
        self.widget.set_window(window_id, widget)

class Interface(object):
    '''
    Wrapper around GlobalInterface with
    window-specific calls added.
    '''
    def __init__(self, window_id=0, global_iface=None):
        if not global_iface:
            global_iface = GlobalInterface()
        self.global_iface = global_iface
        self.window_id = window_id

    def __getattr__(self, name):
        return getattr(self.global_iface, name)

    def set_nextto(self, widget):
        self.make_sure_there_is_a_split()
        which = self.layout[1]
        if which == self.window_id:
            which = self.layout[2]
        self.set_window(which, widget)

class InterfaceWrapper(object):
    def __init__(self, iface):
        self.iface = iface

    def __getattr__(self, name):
        orig = getattr(self.iface, name)
        def wrapper(*args, **kwargs):
            return toolkit.run_in_ui(lambda: orig(*args, **kwargs))

        return wrapper
