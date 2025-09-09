GLOBAL {
	INPUTNAME "player.gt";
	CPU "W65C02";
	COMMENTS 3;
};
SEGMENT { START $8000; END $FFF9; NAME "CODE"; };
SEGMENT { START $FFFA; END $FFFF; NAME "VECTORS"; };

RANGE { START $FFFA; END $FFFF; TYPE AddrTable; };

# it proves less than useful to have ZP handled specially
# LABEL { NAME "zp"; ADDR $0; SIZE $FF; };
LABEL { NAME "stack"; ADDR $100; SIZE $FF; };
LABEL { NAME "aureset"; ADDR $2000; };
LABEL { NAME "aunmi"; ADDR $2001; };
LABEL { NAME "bank"; ADDR $2005; };
LABEL { NAME "auen"; ADDR $2006; };
LABEL { NAME "dma"; ADDR $2007; };
LABEL { NAME "gpad1"; ADDR $2008; };
LABEL { NAME "gpad2"; ADDR $2009; };
LABEL { NAME "dmar_vx"; ADDR $4000; };
LABEL { NAME "dmar_vy"; ADDR $4001; };
LABEL { NAME "dmar_gx"; ADDR $4002; };
LABEL { NAME "dmar_gy"; ADDR $4003; };
LABEL { NAME "dmar_w"; ADDR $4004; };
LABEL { NAME "dmar_h"; ADDR $4005; };
LABEL { NAME "dmar_run"; ADDR $4006; };
LABEL { NAME "dmar_col"; ADDR $4007; };

LABEL { NAME "PLAYHEAD"; ADDR $02; SIZE 2; };
LABEL { NAME "CONST"; ADDR $04; SIZE 2; };
LABEL { NAME "TICKS"; ADDR $06; SIZE 2; };
LABEL { NAME "ADDR"; ADDR $08; SIZE 2; };
LABEL { NAME "OFFSET"; ADDR $0A; SIZE 2; };
LABEL { NAME "SIZE"; ADDR $0C; };
LABEL { NAME "CADDR"; ADDR $0D; SIZE 2; };
