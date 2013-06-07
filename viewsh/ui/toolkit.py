'''
Interface for GUI toolkit used by viewsh GUI.
Currently it is GTK2 and VTE as a terminal emulator.
'''
import gtk
import vte

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

class Terminal:
    def __init__(self):
        self.widget = vte.Terminal()

    def set_pty(self, fd):
        self.widget.set_pty(fd)

def run_in_ui(func):
    gtk.threads_enter()
    try:
        func()
    finally:
        gtk.threads_leave()
