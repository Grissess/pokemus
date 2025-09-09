AS = ca65
LD = ld65

# NB: sequential dependency!
all: au.rom player.gt

au.rom: au/au.o
	$(LD) $(LDFLAGS) $<
au.rom: LDFLAGS += -C au/au.ld
au/au.o: au/au.s

player.gt: src/main.o
	$(LD) $(LDFLAGS) $<
player.gt: LDFLAGS += -C src/main.ld
src/main.o: src/main.s
