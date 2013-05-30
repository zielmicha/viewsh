from abc import ABCMeta, abstractmethod, abstractproperty
from viewsh import task
from select import select

class Stream(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self, data):
        '''
        Asynchronously write data.
        '''

    @abstractmethod
    def set_read_event(self, q):
        '''
        Queue to be called when data arrives using StreamReadEvent.
        '''

    read_event = abstractproperty(fset=set_read_event)

class StreamReadEvent(object):
    def __init__(self, stream, data):
        self.stream = stream
        self.data = data

class StreamCloseEvent(object):
    pass

class FileStream(Stream):
    def __init__(self, input, output, buffer_size=1, select_read=False):
        self.reader = FileStreamReader(input, buffer_size, select_read=select_read)
        self.writer = FileStreamWriter(output)

    def start(self):
        self.reader.start()
        self.writer.start()

    def write(self, data):
        self.writer.q.post(data)

    def set_read_event(self, q):
        self.reader.read_event = q

    def __del__(self):
        self.writer.q.stop()

    read_event = property(fset=set_read_event)

class FileStreamReader(task.Task):
    def __init__(self, input, buffer_size, select_read):
        self.read_event = task.NullQueue()
        self.buffer_size = buffer_size
        self.select_read = select_read
        self.input = input

    def run(self):
        while True:
            if self.select_read:
                _, _, _ = select([self.input], [], [self.input])
            try:
                data = self.input.read(self.buffer_size)
                if not data:
                    raise IOError('EOF')
            except IOError:
                self.read_event.post(StreamCloseEvent())
                return
            else:
                tag = None # TODO
                self.read_event.post(StreamReadEvent(tag, data))

class FileStreamWriter(task.Task):
    def __init__(self, output):
        self.q = task.Queue()
        self.output = output

    def run(self):
        for item in self.q:
            self.output.write(item)
