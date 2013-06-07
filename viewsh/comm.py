import socket
import os
import pickle

from viewsh import state

class Interface(object):
    def is_connected(self):
        return False

    def patch_log(self):
        pass

    def __getattr__(self, name):
        def call(*args, **kwargs):
            return None

        return call

class World(state.State):
    pass
