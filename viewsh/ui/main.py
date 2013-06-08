from viewsh.ui import toolkit
from viewsh.ui import interface
from viewsh.ui.toolkit import Terminal
from viewsh.ui import interface
from viewsh.ui.interface import Interface

from viewsh.comm import World
from viewsh import task
from viewsh import rc

# workaround to properly set signal handlers
from viewsh.transport import local

import pty

def main():
    # todo: argparse
    world = World()
    buffer = create_shell(world=world)
    world[Interface].create_default_layout(buffer)

    toolkit.Main(world[Interface].widget).run()

def create_shell(world):
    term = toolkit.Terminal()
    buffer = world[Interface].create_buffer(term)
    master, slave = pty.openpty()

    term.set_pty(master)
    task.async(lambda: rc.main(fd=slave,
                               buffer=buffer, world=world))
    return buffer

if __name__ == '__main__':
    main()
