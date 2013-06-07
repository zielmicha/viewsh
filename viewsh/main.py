from viewsh.tools import log
from viewsh import rc
from viewsh import comm

def main(fd=0, world=None, interface=None):
    if not world:
        world = comm.World()

    if not interface:
        interface = comm.Interface()

    rc.main(fd, world, interface)

if __name__ == '__main__':
    main()
