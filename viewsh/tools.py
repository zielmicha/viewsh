from __future__ import print_function
import re
import os

def log(*args, **kwargs):
    _log_real(*map(str, args), **kwargs)

_debug_level = int(os.environ.get('DEBUG', 0))

def _log_real(*args, **kwargs):
    level = kwargs.get('level', 0)
    if level <= _debug_level:
        print(*args)

class Exit(BaseException):
    pass

import re
_quote_pos = re.compile('(?=[^-0-9a-zA-Z_./\n])')

def shell_quote(arg):
    if arg:
        return _quote_pos.sub('\\\\', arg).replace('\n',"'\n'")
    else:
        return "''"

def list_to_command(args):
    return ' '.join(map(shell_quote, args))

def as_utf8(arg):
    if isinstance(arg, str):
        return arg
    else:
        return arg.encode('utf8')
