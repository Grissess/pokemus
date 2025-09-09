import sys
from pokemus import *

# the 32-bar chorus of a48

t = Tempo(150)
d = Domain()
a = Animator(1 / Const.VSYNCRATE)

ssaw = WaveLoadEvent.saw(0, 0x300).atten(0.1)
ssaw = ssaw.add(ssaw.harm(2).atten(0.5))
ssaw = ssaw.add(ssaw.harm(4).atten(0.5))
d.add(ssaw)

stri = WaveLoadEvent.tri(0, 0x340).atten(0.2)
stri = stri.add(stri.harm(2))
d.add(stri)

noise = WaveLoadEvent.noise(0, 0x380).atten(0.2)
d.add(noise)

sin = WaveLoadEvent.sin(0, 0x3C0).atten(0.3)
d.add(sin)

stri2 = stri.atten(0.5).moved(0x400)
d.add(stri2)

ssaw2 = ssaw.atten(0.5).moved(0x440)
d.add(ssaw2)


def kick(o):
    for i, tm in enumerate(a.times_points(t.beat(o), 8)):
        ev = PitchEvent.from_frequency(tm, 5, 120 / (1 + i / 2))
        if i == 0:
            ev = ev.start(sin.addr)
        d.add(ev)
    d.add(StopEvent(a.time_after(t.beat(o), 8), 5))

def snare(o):
    d.add(PitchEvent.from_frequency(t.beat(o), 5, 60).start(noise.addr))
    for i, tm in enumerate(a.times_points(t.beat(o), 4)):
        d.add(noise.atten(1 / (1 + i)).at(tm))
    d.add(StopEvent(a.time_after(t.beat(o), 4), 5))

def rhy(o, tail=False, clip=False):
    kick(o)
    kick(o + 0.5)
    snare(o + 1)
    kick(o + 1.75)
    if not clip:
        kick(o + 2.25)
        snare(o + 3)
        if tail:
            kick(o + 3.5)

def wind(o):
    snare(o)
    kick(o + 0.5)
    snare(o + 1)
    kick(o + 1.5)

MELLEAD = [  # half a bar
        (0, 'f,'),
        (0.5, 'g,'),
        (1, 'af'),
        (1.5, 'bf'),
]
MEL1 = [
        (0, 'c'),
        (2.5, 'df'),
        (3.5, 'bf'),
        (6.5, 'r'),
        (8, 'bf'),
        (10.5, 'c'),
        (11.5, 'f,'),
        (14.5, 'r'),
        (16, 'af'),
        (18.5, 'bf'),
        (19.5, 'g,'),
        (22.5, 'r'),
        (24, 'a'),
        (27, 'r'),
]
MEL2 = [
        (0, 'c'),
        (2.5, 'df'),
        (3.5, 'bf'),
        (6.5, 'r'),
        (8, 'bf'),
        (10.5, 'c'),
        (11.5, 'f'),
        (14.5, 'r'),
        (16, 'af'),
        (18.5, 'bf'),
        (19.5, 'g,'),
        (22.5, 'r'),
        (24, 'a'),
        (27, 'r'),
]

ARPS = [
        ("df'", "bf'", 'f', 'df'),
        ("bf'", 'g', 'df', 'bf'),
        ("a'", 'f', 'c', 'a'),
        ("af'", 'f', 'c', 'af'),
        ('g', 'f', 'c', 'bf'),
        ('g', 'ef', 'bf', 'g,'),
        ("a'", 'f', 'c', 'a'),
        ("a'", 'f', 'c', 'a'),
]
def arp(seq, origin, reps=4, intime=4):
    full = list(seq) * reps
    return [
            (origin + i * intime / len(full), v)
            for i, v in enumerate(full)
    ]

ARP = sum(
        (arp(seq, i * 4)
        for i, seq in enumerate(ARPS)),
        start=[]
)

def b1rhy(o, p):
    return [
            (o + 0, p),
            (o + 0.75, 'r'),
            (o + 1, p),
            (o + 1.5, 'r'),
            (o + 1.75, p),
            (o + 2.25, 'r'),
            (o + 2.5, p),
            (o + 3, 'r'),
            (o + 3.5, p),
    ]

def b2rhy(o, p):
    return [
            (o + 0, p),
            (o + 0.75, 'r'),
            (o + 1, p),
            (o + 1.25, 'r'),
            (o + 1.5, p),
            (o + 1.625, 'r'),
            (o + 1.75, p),
            (o + 2, 'r'),
            (o + 2.25, p),
            (o + 2.375, 'r'),
            (o + 2.5, p),
            (o + 3.25, 'r'),
            (o + 3.5, p),
    ]


BASS1 = (
        b1rhy(0, 'df,') +
        b1rhy(4, 'bf,') +
        b1rhy(8, 'a,') +
        b1rhy(12, 'af,') +
        b1rhy(16, 'g,,') +
        b1rhy(20, 'ef,,') +
        b1rhy(24, 'f,,') +
        b1rhy(28, 'f,,')
)
BASS2 = (
        b2rhy(0, 'df,') +
        b2rhy(4, 'bf,') +
        b2rhy(8, 'a,') +
        b2rhy(12, 'af,') +
        b2rhy(16, 'g,,') +
        b2rhy(20, 'ef,,') +
        b2rhy(24, 'f,,') +
        b2rhy(28, 'f,,')
)

LEAD1 = Instrument(0, stri.addr)
LEAD2 = Instrument(0, ssaw.addr)
BL = Instrument(1, stri.addr)
ARI1 = Instrument(2, stri2.addr)
ARI2 = Instrument(2, ssaw2.addr)

# Song
for i in range(0, 32, 4):
    rhy(i, tail=i % 8 == 4)
LEAD1.legato(d, t.beat, 0, MEL1)
ARI1.legato(d, t.beat, 0, ARP)
BL.legato(d, t.beat, 0, BASS1)
LEAD1.legato(d, t.beat, 30, MELLEAD)

for i in range(32, 60, 4):
    rhy(i, tail=i % 8 == 4)
rhy(60, clip=True)
wind(62)
LEAD1.legato(d, t.beat, 32, MEL2)
ARI1.legato(d, t.beat, 32, ARP)
BL.legato(d, t.beat, 32, BASS1)
LEAD2.legato(d, t.beat, 62, MELLEAD)

for i in range(64, 96, 4):
    rhy(i, tail=i % 8 == 4)
LEAD2.legato(d, t.beat, 64, MEL1)
ARI2.legato(d, t.beat, 64, ARP)
BL.legato(d, t.beat, 64, BASS2)
LEAD2.legato(d, t.beat, 94, MELLEAD)

for i in range(96, 128, 4):
    rhy(i, tail=i % 8 == 4)
LEAD2.legato(d, t.beat, 96, MEL2)
ARI2.legato(d, t.beat, 96, ARP)
BL.legato(d, t.beat, 96, BASS2)
LEAD1.legato(d, t.beat, 126, MELLEAD)

d.add(EndEvent(t.beat(128)))

#d.to_poke_script(sys.stdout)
d.to_rom_patch(sys.stdout.buffer)
