MEMORY {
	RAM: start = $0000, size = $1000, file = "au.rom";
}

SEGMENTS {
	ZP: load = RAM, type = bss, start = $0000;
	STACK: load = RAM, type = bss, start = $0100;
	CODE: load = RAM, type = rw, start = $0200;
	VECTORS: load = RAM, type = ro, start = $0FFA;
}
