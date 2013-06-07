from viewsh.tools import log
from Queue import Queue as _Queue
import threading
import traceback
import sys
import os

from functools import partial

class Queue(object):
    def __init__(self, name='queue'):
        self._q = _Queue(0)
        self._senitel = type('SenitelTuple', (tuple,), {})
        self._stopped = False
        self._name = name

    def post(self, item):
        self._q.put(item)

    def get(self, timeout=None):
        '''
        Fetch a value from queue. Raises StopIteration if
        queue is stopped. Calls function added by call_in_queue.
        '''
        if self._stopped:
            raise StopIteration()

        while True:
            value = self._q.get(timeout=timeout)
            if not isinstance(value, self._senitel):
                break
            if value[0] == 'stop':
                raise StopIteration()
            elif value[0] == 'call':
                value[1]()

        return value

    def stop(self):
        # works only if there is one thread waiting!
        self._stopped = True
        self._q.put(self._senitel(['stop']))

    def call_in_queue(self, func):
        self._q.put(self._senitel(['call', func]))

    def __iter__(self):
        while True:
            yield self.get()

    def __repr__(self):
        return '<Queue: %s at 0x%X>' % (self._name, id(self))

class NullQueue(object):
    def post(self, item):
        pass

class Task(object):
    def __init__(self):
        self.thread = None
        self.lock = threading.Lock()

    def start(self, daemon=True):
        log("starting %r" % self, level=3)
        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = daemon
        self.thread.start()

    def __finish(self):
        log("finishing %r" % self, level=3)

    def __run(self):
        try:
            self.run()
        except BaseException as err:
            # normally, there is no point to continue
            if not isinstance(err, (SystemExit, KeyboardInterrupt)):
                traceback.print_exc()
            if not os.environ.get('ERROR_NOEXIT'):
                sys.exitfunc()
                os._exit(1)
        self.__finish()

class async(Task):
    ''' Run func in separete thread. '''
    def __init__(self, func):
        Task.__init__(self)
        self.run = func
        self.start()

class AsyncCall(object):
    '''
    Single asynchronous call. If call is called twice, result of first call won't be
    returned.
    '''
    def __init__(self, target_queue):
        self.target_queue = target_queue
        self.current_call_id = 0

    def call(self, func, and_then=None):
        '''
        Call func in separete thread. After completion
        call and_then in target_queue.
        '''
        self.abort()
        call_id = self.current_call_id

        def pass_result(result):
            if call_id == self.current_call_id:
                and_then(result)

        def wrapper():
            result = func()
            if and_then:
                self.target_queue.call_in_queue(
                    partial(pass_result, result))

        async(wrapper)

    def abort(self):
        self.current_call_id += 1
