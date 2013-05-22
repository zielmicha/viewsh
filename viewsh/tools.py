from __future__ import print_function

def log(*args):
    _log_real(*args)

def _log_real(*args):
    # don't clobber terminal output
    pass # print('LOG', *args)
