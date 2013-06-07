from viewsh.tools import log
from viewsh import rc
from viewsh import comm

def main(fd=0, interface=None):
    world = comm.World()
    if interface:
        world[comm.Interface] = interface

    rc.main(fd, world)

if __name__ == '__main__':
    main()
