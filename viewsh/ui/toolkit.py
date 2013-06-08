'''
Interface for GUI toolkit used by viewsh GUI.
Currently it is GTK2 and VTE as a terminal emulator.
'''
import gtk
import glib
import vte
import threading
import sys

# <warning>
# DO THIS OR YOUR INTERPRATETER WILL GO INSANE
# AND MAKE REALLY OBSCURE AND COUNTERINTUITIVE
# BUGS IF YOU USE THREADS
import gobject
gobject.threads_init()
gtk.gdk.threads_init() # not sure if needed
# </warning>

from viewsh import task

class Main(task.Task):
    def __init__(self, main):
        self.main = main

    def run(self):
        window = gtk.Window()
        window.add(self.main.widget)
        window.connect('delete-event', self.quit)
        window.show_all()
        gtk.main()

    def quit(self, *args):
        gtk.main_quit()

class _ToolkitWidget(object):
    pass

class Terminal(_ToolkitWidget):
    def __init__(self, height=30):
        self.widget = vte.Terminal()
        self.widget.set_size(80, height)

    def set_pty(self, fd):
        self.widget.set_pty(fd)

class _Replacable(_ToolkitWidget):
    def __init__(self):
        self.widget = gtk.HBox()
        self._last_widget = None
        self._set_widget(gtk.Label('nothing there'))

    def _set_widget(self, widget):
        # Ok. You need to show widget to make it visible.
        # Couldn't all these default values be saner?
        # So when you add a widget to container it will be
        # there?
        widget.show()
        if self._last_widget:
            self.widget.remove(self._last_widget)

        self._last_widget = widget
        if widget:
            self.widget.add(widget)

class Label(_ToolkitWidget):
    def __init__(self, text):
        self.widget = gtk.Label(text)

class MultiWindow(_Replacable):
    def __init__(self):
        _Replacable.__init__(self)
        self.windows = {}
        self.window_values = {}

    def set_layout(self, layout):
        self.windows = {}
        layout_widget = build_layout(layout, self.windows)
        self._set_widget(layout_widget.widget)
        for id, widget in self.window_values.items():
            self.set_window(id, widget)

    def set_window(self, i, widget):
        self.windows[i]._set_widget(widget.widget)
        self.window_values[i] = widget

def build_layout(node, windows_out):
    if isinstance(node, int):
        wnd = Window(node)
        windows_out[node] = wnd
        return wnd
    elif isinstance(node, tuple):
        kind = node[0]
        args = node[1:]
        if kind in ('hsplit', 'vsplit'):
            way = kind[0]
            children = [ build_layout(arg, windows_out).widget for arg in args ]
            return Split(way, children)
        else:
            raise TypeError(node)
    else:
        raise TypeError(node)

class Split(_ToolkitWidget):
    def __init__(self, kind, children):
        self.widget = gtk.VPaned() if kind == 'v' else gtk.HPaned()
        child1, child2 = children
        child1.show()
        child2.show()
        self.widget.add1(child1)
        self.widget.add2(child2)

class Window(_Replacable):
    def __init__(self, id):
        _Replacable.__init__(self)
        self.id = id

def run_in_ui(func):
    gtk.threads_enter()
    try:
        func()
    finally:
        gtk.threads_leave()
