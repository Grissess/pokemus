import sys
from pokemus import Const

inp = sys.stdin.buffer
def u16():
    return int.from_bytes(inp.read(2), 'little')
def u8():
    return int.from_bytes(inp.read(1))

stoff = u16()
print('Const offset:', stoff)

total_ticks = 0

offs = set()
while True:
    ticks = u16()
    if ticks == 0xFFFF:
        print('Script done; constants follow:')
        break
    total_ticks += ticks
    print(f'{total_ticks:04X}/{total_ticks / Const.VSYNCRATE}s: Wait {ticks:04X} ticks, then:')
    while True:
        addr = u16()
        if addr == 0:
            break
        ln = u8()
        off = u16()
        offs.add(off)
        print(f'- Write {ln:02X} bytes from const {off:04X} to {addr:04X}')

offs = sorted(offs)
for idx, start in enumerate(offs):
    if idx < len(offs) - 1:
        ln = offs[idx + 1] - start
    else:
        ln = -1
    print(f'- {start:04X}: {inp.read(ln).hex()}')
