from viewsh.ui import toolkit
from viewsh.ui import interface
from viewsh.ui import comm
from viewsh import main as shell_main
from viewsh import task
from viewsh.ui.toolkit import Terminal

# workaround to properly set signal handlers
from viewsh.transport import local

import pty

def main():
    # todo: argparse
    iface = interface.Interface()
    term = create_shell(iface)
    iface.create_default_layout(term)

    toolkit.Main(iface.widget).run()

def create_shell(iface, world=None):
    master, slave = pty.openpty()

    term = toolkit.Terminal()
    term.set_pty(master)
    task.async(lambda: shell_main.main(fd=slave, interface=iface, world=world))
    return term

if __name__ == '__main__':
    main()
