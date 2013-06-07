from viewsh import rc
from viewsh import comm

def main(fd=0, interface=None):
    world = comm.World()
    if interface:
        world[comm.Interface] = interface
    world[comm.Interface].patch_log()

    rc.main(fd, world)

if __name__ == '__main__':
    main()
