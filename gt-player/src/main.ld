MEMORY {
	RAM: start = $0000, size = $2000;
	IO: start = $2000, size = $1000;
	AURAM: start = $3000, size = $1000;
	GFX: start = $4000, size = $4000;
	ROM: start = $8000, size = $8000, file = "player.gt";
}

SEGMENTS {
	CODE: load = ROM, type = ro;
	RODATA: load = ROM, type = ro;
	DATA: load = ROM, run = RAM, type = rw, start = $0200, define = yes;
	BSS: load = RAM, type = bss, define = yes;
	VECTORS: load = ROM, type = ro, start = $FFFA;
}
