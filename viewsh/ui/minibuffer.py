from viewsh.ui.interface import Interface
from viewsh import terminal
from viewsh import task

class MiniBuffer(task.Task):
    pass_state = True

    def __init__(self, world, fd):
        self.world = world
        self.terminal = terminal.Terminal(fd)
        self.terminal.start()

    def run(self):
        self.terminal.write('minibuffer$ ')

def create(world):
    slave, buffer = world[Interface].create_terminal_buffer(height=1)
    world[MiniBuffer] = MiniBuffer(world, slave)
    world[MiniBuffer].start()
    world[Interface].set_window(-1, buffer)
