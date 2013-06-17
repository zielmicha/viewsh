from viewsh.ui import toolkit
from viewsh.ui import interface
from viewsh.ui.toolkit import Terminal
from viewsh.ui import interface
from viewsh.ui.interface import Interface
from viewsh.ui import minibuffer

from viewsh.comm import World
from viewsh import task
from viewsh import rc

def main():
    # todo: argparse
    world = World()
    buffer = create_shell(world=world)
    world[Interface].create_default_layout(buffer)
    minibuffer.create(world)

    toolkit.Main(world[Interface].widget).run()

def create_shell(world):
    slave, buffer = world[Interface].create_terminal_buffer()
    task.async(lambda: rc.main(fd=slave,
                               buffer=buffer, world=world))
    return buffer

if __name__ == '__main__':
    main()
