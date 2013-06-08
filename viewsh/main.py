from viewsh.tools import log
from viewsh import rc
from viewsh import comm
from viewsh.ui.interface import Interface

class UINotAvailable(object):
    def __getattr__(self, name):
        raise ValueError('UI is not available')

def main():
    world = comm.World()
    world[Interface] = UINotAvailable()
    rc.main(0, world, UINotAvailable())

if __name__ == '__main__':
    main()
