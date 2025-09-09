# pokemus

_"POKE music"_

This is a _very_ experimental project for converting descriptions of music into
a linear stream of events over time. Right now, it's set up for the
[GameTank][gt], but this project was conceived a while ago for the GameBoy
Color. Who knows, maybe that will still get support, too.

[gt]: https://gametank.zone/

## Usage

_the world's worst tracker_

`pokemus` is intended to be an importable module. It has no dependencies on
non-stdlib Python. In short, one usually:

- creates a `Domain`, which represents a scheduling domain to which one can
  `.add` `Event`s (which are, essentially, memory pokes scheduled for a certain
  time);

- (usually) creates a `Tempo` for managing a song's rhythmic mapping to real
  time;

- (usually) creates an `Animator` for doing slides (in pitch, in frequency,
  etc.).

There are examples included in the repository. Running each of them will write
a binary blob to `stdout` which can be loaded by the player.

```
python3 example2.py > song.rom
```

If you want, since this project was meant to be used with [gt-aemu][aemu], you
swap the writing portion at the end of the example scripts.

```python
d.to_poke_script(sys.stdout)
#d.to_rom_patch(sys.stdout.buffer)
```

This will generate a "poke script" of the form that `emu.py` from `gt-aemu`
expects.

[aemu]: https://github.com/Grissess/gt-aemu

## Playing

There are two components to playing a song:

- The generator ROM, whose structures are hard-coded; and
- a driver program, the "player", that follows the poke script.

Both of these are in `gt-player`; a [README][player] documents further
instructions for building therein. You'll want the ROM, at least, for
`gt-aemu`.

[player]: ./gt-player

## Utilities

`dump.py` implements a debug inspector of pokemus ROM patches. You can use this
to figure out what the script would seem to do in plain language.

`rom_to_script.py` implements a converter from ROM patches to gt-aemu
pokescripts. Note that the conversion isn't perfect--the timebase for gt-aemu
is samples, whereas it's VSYNC clocks (~60Hz) for ROM patches, so you'll lose a
little precision in this process.
