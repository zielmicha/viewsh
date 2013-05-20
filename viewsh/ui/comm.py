from viewsh import task

import os
import pty
import socket
import tempfile
import threading
import atexit
import pickle

class Server(task.Task):
    def __init__(self, iface):
        self.server_started = threading.Event()
        self.iface = iface

    def run(self):
        sock = socket.socket(socket.AF_UNIX)
        self.sock_path = self.bind_socket(sock)
        sock.listen(1)
        self.server_started.set()
        import sys
        while True:
            client, addr = sock.accept()
            #threading.Thread(target=self.handle, args=[client]).start()
            self.handle(client)
            del client

    def handle(self, sock):
        f = sock.makefile('r+')
        data = pickle.load(f)
        result = self.call(data)
        pickle.dump(result, f)
        f.close()
        sock.close()

    def call(self, data):
        # unsafe
        return getattr(self.iface, data[0])(*data[1], **data[2])

    def bind_socket(self, sock):
        # anonymously bind socket
        dir = tempfile.mkdtemp()
        path = dir + '/socket'
        sock.bind(path)
        def delete():
            os.unlink(path)
            os.rmdir(dir)

        atexit.register(delete)
        return path

    def fork_shell(self):
        self.server_started.wait()
        pid, fd = pty.fork()
        if pid == 0:
            # child
            os.environ['VIEWSH_SOCKET'] = self.sock_path
            os.chdir(os.path.dirname(__file__) + '/../..')
            os.execvp('python', ['python', '-m', 'viewsh.shell'])
        else:
            return fd
