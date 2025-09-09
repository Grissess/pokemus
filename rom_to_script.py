import sys
from pokemus import Const

AVCONV = Const.SAMPRATE / Const.VSYNCRATE

romfile, scriptfile = sys.argv[1:]

rf, sf = open(romfile, 'rb'), open(scriptfile, 'w')
def readu(bts):
    return int.from_bytes(rf.read(bts), 'little')

total_ticks = 0
coff = readu(2)
while True:
    ticks = readu(2)
    if ticks == 0xFFFF:
        break
    total_ticks += ticks
    while True:
        addr = readu(2)
        if addr == 0:
            break
        addr -= 0x3000  # XXX hardcoded AURAM offset
        ln = readu(1)
        off = readu(2)
        here = rf.tell()
        rf.seek(coff + off)
        print(f'{hex(int(AVCONV * total_ticks))}:{hex(addr)}={rf.read(ln).hex()}', file=sf)
        rf.seek(here)
