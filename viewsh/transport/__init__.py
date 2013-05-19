from abc import ABCMeta, abstractmethod

class Transport(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, args):
        '''
        Executes command specified as list args. Returns Stream instance.
        '''
