# gt-player for pokemus

This is a GameTank player cartridge and audio ROM for pokemus music, as
structured at present.

For starters, you'll need to put a `song.rom` in this directory. The scripts in
the `pokemus` root will generate one. So, for example:

```
python3 ../example2 > song.rom
```

Then grab the [cc65][cc65] toolchain (you'll need it for most GT cart SDKs anyway),
ensure it's in PATH or otherwise accessible, and run `make` in this directory.
You'll get two artifacts:

- `au.rom` is an ACP ROM, suitable for (for example) [gt-aemu][aemu].
- `player.gt` is a 32k cartridge--also generally safe to load onto 2M
  flashcarts. You can run this in the emulator, or on real hardware.

[cc65]: https://cc65.github.io/doc/
[aemu]: https://github.com/Grissess/gt-aemu
