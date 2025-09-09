import os, math, sys

class Const:
    V_BASE = 0x10
    V_SIZE = 0x06
    V_PHVEL = 0x02
    V_TBL = 0x04
    SAMPRATE = 44192
    VSYNCRATE = 60

class Tempo:
    def __init__(self, bpm):
        self.bpm = bpm

    def beat(self, f):
        return f * 60 / self.bpm

class Animator:
    def __init__(self, quantum):
        self.quantum = quantum

    def times_points(self, origin, n):
        for i in range(n):
            yield origin + i * self.quantum

    def time_after(self, origin, n):
        return origin + n * self.quantum

    def times_range(self, origin, width):
        yield from self.times_points(origin, int(width / self.quantum))

class Domain:
    def __init__(self):
        self.events = {}

    def add(self, ev):
        self.events.setdefault(ev.time, []).append(ev)

    def linearize(self):
        return sorted(self.events.items(), key=lambda pair: pair[0])

    def to_poke_script(self, f):
        for tm, evs in self.linearize():
            for ev in evs:
                for addr, val in ev.pokes():
                    print(f'0x{round(tm * Const.SAMPRATE):X}:0x{addr:X}={val.hex().upper()}', file=f)

    def to_rom_patch(self, f, repack_adjacent=True):
        stab = bytearray()
        last_tm = 0
        f.write(b'\0\0')  # reserve space
        for tm, evs in self.linearize():
            dt = (tm - last_tm) * Const.VSYNCRATE
            last_tm = tm
            f.write(round(dt).to_bytes(2, 'little'))

            pokes = []
            for ev in evs:
                pokes.extend(ev.pokes())

            if repack_adjacent:
                new_pokes = []
                ix = 0
                pokes.sort(key=lambda pair: pair[0])  # sort by addr
                while ix < len(pokes):
                    addr, val = pokes[ix]
                    ix += 1
                    while ix < len(pokes):
                        # Are the segments adjacent or overlapping?
                        naddr, nval = pokes[ix]
                        if naddr > addr + len(val):
                            new_pokes.append((addr, val))
                            break # nope
                        # Merge values (discard any overwritten portion)
                        val = val[:naddr] + nval
                        # And repeat
                        ix += 1
                # We fall off this loop with one last poke remaining, emplace it now
                new_pokes.append((addr, val))
                #print('old', pokes, file=sys.stderr)
                #print('new', new_pokes, file=sys.stderr)
                pokes = new_pokes

            # Check to make sure none of our pokes are too large to
            # encode--rather than using a larger len field, it's more efficient
            # to just split them into multiple records, since large pokes are
            # exceptional
            new_pokes = []
            for addr, val in pokes:
                while len(val) > 255:
                    new_pokes.append((addr, val[:255]))
                    addr, val = addr + 255, val[255:]
                new_pokes.append((addr, val))
            pokes = new_pokes

            for addr, val in pokes:
                off = stab.find(val)
                if off == -1:
                    off = len(stab)
                    stab.extend(val)
                f.write((0x3000 + addr).to_bytes(2, 'little'))  # XXX hardcoded ARAM
                f.write(len(val).to_bytes(1))
                f.write(off.to_bytes(2, 'little'))
            f.write(b'\0\0')
        f.write(b'\xff\xff')
        stoff = f.tell()  # NB: this needs to be in byte units--is that not true on all plats?
        #print('stoff', stoff, file=sys.stderr)
        f.write(stab)
        f.seek(0, 0)
        f.write(stoff.to_bytes(2, 'little'))

class Event:
    def __init__(self, time):
        self.time = time

    def at(self, nt):
        return type(self)(nt)

    def pokes(self):
        raise NotImplementedError()

class PitchEvent(Event):
    def __init__(self, time, voice, period):
        super().__init__(time)
        self.voice, self.period = voice, period

    @classmethod
    def from_frequency(cls, time, voice, frq):
        return cls(time, voice, round(frq * 0xFFFF / Const.SAMPRATE))

    @classmethod
    def from_midi(cls, time, voice, pitch):
        return cls.from_frequency(time, voice, 440 * 2 ** ((pitch - 69) / 12))

    PITCHES = {'a': 57, 'b': 59, 'c': 60, 'd': 62, 'e': 64, 'f': 65, 'g': 67}
    TRANSPOSE = 0
    @classmethod
    def from_lynote(cls, time, voice, note):
        base = cls.PITCHES[note[0]] + cls.TRANSPOSE
        base += 12 * (note.count("'") - note.count(','))
        if len(note) > 1 and note[1] == 's':
            base += 1
        elif len(note) > 1 and note[1] == 'f':
            base -= 1
        return cls.from_midi(time, voice, base)

    def start(self, tbl):
        return PlayEvent(self.time, self.voice, self.period, tbl)

    def at(self, nt):
        return type(self)(nt, self.voice, self.period)

    def pokes(self):
        return [(Const.V_BASE + Const.V_SIZE * self.voice + Const.V_PHVEL, self.period.to_bytes(2, 'little'))]

class PlayEvent(PitchEvent):
    def __init__(self, time, voice, period, tbl):
        super().__init__(time, voice, period)
        self.tbl = tbl

    def at(self, nt):
        return type(self)(nt, self.voice, self.period, self.tbl)

    def pokes(self):
        return [(Const.V_BASE + Const.V_SIZE * self.voice + Const.V_TBL, (0x8000 | self.tbl).to_bytes(2, 'little'))] + super().pokes()

class StopEvent(Event):
    def __init__(self, time, voice):
        super().__init__(time)
        self.voice = voice

    def at(self, nt):
        return type(self)(nt, self.voice)

    def pokes(self):
        return [(Const.V_BASE + Const.V_SIZE * self.voice + Const.V_TBL, b'\0\0')]

class EndEvent(Event):
    def pokes(self):
        return [(0, b'')]  # special signal to the emulator

class WaveLoadEvent(Event):
    def __init__(self, time, addr, buf):
        super().__init__(time)
        self.addr, self.buf = addr, buf

    @classmethod
    def saw(cls, time, addr):
        return cls(time, addr, bytes(round((127 * ((i - 32) / 32)) % 0x100) for i in range(64)))

    @classmethod
    def sin(cls, time, addr):
        return cls(time, addr, bytes(round(127 * math.sin(math.tau * (i / 64))) % 0x100 for i in range(64)))

    @classmethod
    def sqr(cls, time, addr, dc=0.5):
        return cls(time, addr, bytes(0x80 if (i / 64) < dc else 0x7F for i in range(64)))

    @classmethod
    def tri(cls, time, addr):
        return cls(time, addr, bytes(round((127 * ((i - 16) / 16 if i < 32 else (48 - i) / 16)) % 0x100) for i in range(64)))

    @classmethod
    def noise(cls, time, addr):
        return cls(time, addr, os.urandom(64))

    def atten(self, amt):
        arr = bytearray(self.buf)
        for idx, i in enumerate(arr):
            si = i - 0x100 if i & 0x80 else i
            arr[idx] = round(amt * si) % 0x100
        return type(self)(self.time, self.addr, bytes(arr))

    def add(self, other):
        arr = bytearray(self.buf)
        for idx, i in enumerate(arr):
            si = i - 0x100 if i & 0x80 else i
            o = other.buf[idx]
            so = o - 0x100 if o & 0x80 else o
            arr[idx] = (i + o) % 0x100
        return type(self)(self.time, self.addr, bytes(arr))

    def harm(self, n):
        arr = bytearray(64)
        for idx in range(len(arr)):
            arr[idx] = self.buf[(idx * n) % len(self.buf)]
        return type(self)(self.time, self.addr, bytes(arr))

    def moved(self, naddr):
        return type(self)(self.time, naddr, self.buf)

    def at(self, nt):
        return type(self)(nt, self.addr, self.buf)

    def pokes(self):
        return [(self.addr, self.buf)]

class Instrument:
    def __init__(self, voice, tbl):
        self.voice, self.tbl = voice, tbl

    def legato(self, domain, tempo, origin, notes):
        playing = False
        for time, pitch in notes:
            if pitch == 'r':
                if playing:
                    domain.add(StopEvent(tempo(origin + time), self.voice))
                    playing = False
            else:
                ev = PitchEvent.from_lynote(tempo(origin + time), self.voice, pitch)
                if not playing:
                    ev = ev.start(self.tbl)
                    playing = True
                domain.add(ev)
