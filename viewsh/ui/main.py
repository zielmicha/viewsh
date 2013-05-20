from viewsh.ui import toolkit
from viewsh.ui import interface
from viewsh.ui import comm

def main():
    term = toolkit.Terminal()
    iface = interface.Interface()
    serv = comm.Server(iface)
    serv.start()
    pty_fd = serv.fork_shell()
    term.set_pty(pty_fd)
    toolkit.Main(term).run()

if __name__ == '__main__':
    main()
