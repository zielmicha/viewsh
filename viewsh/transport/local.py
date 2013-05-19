from viewsh import transport

class LocalTransport(transport.Transport):
    def __init__(self):
        super(LocalTransport, self).__init__()
