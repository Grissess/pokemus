import sys
from pokemus import *

# an 8-bar portion of a49

a = Animator(1 / Const.VSYNCRATE)
t = Tempo(180)
b = t.beat
d = Domain()
n = PitchEvent.from_lynote
s = StopEvent

saw = WaveLoadEvent.saw(0, 0x300).atten(0.1)
saw = saw.add(saw.harm(2))
d.add(saw)
ns = WaveLoadEvent.noise(0, 0x340).atten(0.2)
d.add(WaveLoadEvent.sin(0, 0x380).atten(0.3))

#PitchEvent.TRANSPOSE = 12

def k(o):
    for i, t in enumerate(a.times_points(b(o), 4)):
        ev = PitchEvent.from_frequency(t, 3, 80 / (1 + i))
        if i == 0:
            ev = ev.start(0x380)
        d.add(ev)
    d.add(s(a.time_after(b(o), 4), 3))

def sn(o):
    ev = PitchEvent.from_frequency(b(o), 3, 60).start(0x340)
    d.add(ev)
    for i, t in enumerate(a.times_points(b(o), 4)):
        d.add(ns.atten(1 / (1 + i)).at(t))
    d.add(s(a.time_after(b(o), 4), 3))

def rhy(o):
    sn(o + 0)
    k(o + 0.5)
    k(o + 1)
    k(o + 1.75)
    sn(o + 2)
    k(o + 2.5)
    k(o + 3.5)
    #sn(o + 4)  # next iter

meli = Instrument(0, 0x300)
def mel(o):
    meli.legato(d, b, o, [
        (0, 'g'),
        (0.5, 'gf'),
        (1, "bf'"),
        (1.5, 'b'),
        (2, 'e'),
        (2.5, 'gf'),
        (3, 'df'),
        (3.5, 'd'),
        (4, 'a'),
        (4.5, 'g,'),
        (5, 'gf,'),
        (6, 'r'),
    ])

def mel2(o):
    meli.legato(d, b, o, [
        (0, 'gf'),
        (0.5, 'e'),
        (1, "bf'"),
        (1.5, 'b'),
        (2, 'gf'),
        (2.5, 'g'),
        (3, 'd'),
        (3.5, 'e'),
        (4, 'a'),
        (4.5, 'g,'),
        (5, 'gf,'),
        (6, 'r'),
    ])

for i in range(0, 32, 4):
    rhy(i)
mel(0)
d.add(n(b(1), 1, 'b,').start(0x300))
d.add(n(b(1), 2, 'd,,').start(0x300))

mel(8)
d.add(n(b(9), 1, 'a,'))

mel2(16)
d.add(n(b(17), 1, 'b,'))
d.add(n(b(17), 2, 'e,,'))

mel(24)
d.add(n(b(25), 1, 'df,'))
d.add(n(b(25), 2, 'gf,,'))

d.add(EndEvent(b(32)))

#d.to_poke_script(sys.stdout)
d.to_rom_patch(sys.stdout.buffer)
