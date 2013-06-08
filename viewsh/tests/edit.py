from .emulator import Emulator
import time

emu = Emulator()
emu.expect('/ $')

backspace = '\x7f'

emu = Emulator()
emu.expect('/ $')
emu.type('foobar')
emu.expect('/ $ foobar')
emu.type(backspace * 6)
emu.expect('/ $')

emu = Emulator()
emu.expect('/ $')
emu.type('abcd' * 10)
emu.expect('/ $ ' + 'abcd' * 8 + 'abc', 'dabcd')
emu.type(backspace * 5)
emu.expect('/ $ ' + 'abcd' * 8 + 'abc', '')
emu.type(backspace)
emu.expect('/ $ ' + 'abcd' * 8 + 'ab', '')
emu.type(backspace * 50)
emu.expect('/ $')

emu = Emulator()
emu.expect('/ $')
emu.type('abcd' * 10)
emu.expect('/ $ ' + 'abcd' * 8 + 'abc', 'dabcd')
emu.type('\x1b[D' * 7)
emu.type('Z')
emu.expect('/ $ ' + 'abcd' * 8 + 'aZb', 'cdabcd')
emu.type('Z' * 10)
emu.expect('/ $ ' + 'abcd' * 8 + 'aZZ', 'Z' * 9 + 'bcdabcd')
emu.type('Z' * 39)
emu.expect('/ $ ' + 'abcd' * 8 + 'aZZ', 'Z' * 39, 'Z' * 9 + 'bcdabcd')

emu = Emulator()
emu.expect('/ $')
emu.type('abcd' * 10)
emu.expect('/ $ ' + 'abcd' * 8 + 'abc', 'dabcd')
emu.type('\x1b[D' * 7)
emu.type('\x1b[C' * 5)
emu.type('Z')
emu.expect('/ $ ' + 'abcd' * 8 + 'abc', 'dabZcd')
