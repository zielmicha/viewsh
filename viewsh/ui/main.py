from viewsh.ui import toolkit
from viewsh.ui import interface
from viewsh.ui import comm
from viewsh import main as shell_main
from viewsh import task
import pty

def main():
    # todo: argparse
    import os
    debug_level = int(os.environ.get('DEBUG', 0))

    master, slave = pty.openpty()
    iface = interface.Interface()
    iface.create_default_shell(master)

    toolkit.Main(iface.widget).start(daemon=False)

    shell_main.main(fd=slave, interface=interface.InterfaceWrapper(iface))

if __name__ == '__main__':
    main()
