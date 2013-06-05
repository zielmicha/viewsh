from viewsh import rc
from viewsh import comm

def main():
    world = comm.World()
    world[comm.Interface].patch_log()

    rc.main(0, world)

if __name__ == '__main__':
    main()
