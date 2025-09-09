.SETCPU "W65C02"

GT_AURESET = $2000
GT_BANK = $2005
GT_AURATE = $2006
GT_DMA = $2007

GT_VIA = $2800
.STRUCT VIA
	XRB .BYTE
	XRA .BYTE
	DDRB .BYTE
	DDRA .BYTE
	T1C .WORD
	T1L .WORD
	T2C .WORD
	SR .BYTE
	ACR .BYTE
	PCR .BYTE
	IFR .BYTE
	IER .BYTE
	XRAD .BYTE
.ENDSTRUCT

GT_AURAM = $3000

GT_DMAR_VX = $4000
GT_DMAR_VY = $4001
GT_DMAR_GX = $4002
GT_DMAR_GY = $4003
GT_DMAR_W = $4004
GT_DMAR_H = $4005
GT_DMAR_RUN = $4006
GT_DMAR_COL = $4007

GT_DMAF_ENABLE = $01
GT_DMAF_ALTFB = $02
GT_DMAF_NMI = $04
GT_DMAF_COLFILL = $08
GT_DMAF_TILE = $10
GT_DMAF_FB = $20
GT_DMAF_IRQ = $40
GT_DMAF_OPAQUE = $80

GT_HUE_GREEN = $00
GT_HUE_YELLOW = $20
GT_HUE_ORANGE = $40
GT_HUE_RED = $60
GT_HUE_MAGENTA = $80
GT_HUE_INDIGO = $A0
GT_HUE_BLUE = $C0
GT_HUE_CYAN = $E0
GT_HUE_MASK = $E0

GT_SAT_NONE = $00
GT_SAT_SOME = $08
GT_SAT_MORE = $10
GT_SAT_FULL = $18
GT_SAT_MASK = $18

PLAYHEAD = $02
CONST = $04
TICKS = $06
ADDR = $08
OFFSET = $0A
SIZE = $0C
CADDR = $0D

.CODE

AUROM:
	.incbin "../au.rom"

SONG:
	.incbin "../song.rom"

RESET:
	SEI
	CLD
	LDX #$FF
	TXS
	STZ GT_BANK
	CLI

	; may as well clear the screen while we're at it
	LDA #(GT_DMAF_ENABLE | GT_DMAF_COLFILL | GT_DMAF_IRQ | GT_DMAF_OPAQUE)
	STA GT_DMA

.MACRO cls color
	LDA #$7F
	LDX #<~(color)
	STA GT_DMAR_W
	STA GT_DMAR_H
	STX GT_DMAR_COL
	STZ GT_DMAR_VX
	STZ GT_DMAR_VY

	LDX #1
	STX GT_DMAR_RUN
	WAI
	STA GT_DMAR_VX
	STX GT_DMAR_RUN
	WAI
	STA GT_DMAR_VY
	STX GT_DMAR_RUN
	WAI
	STZ GT_DMAR_VX
	STX GT_DMAR_RUN
	WAI
.ENDMACRO
	cls $00

	STZ GT_DMA  ; kill IRQ/NMI for now while we set up

	STZ GT_AURATE
.MACRO pagecpy dst, org
.LOCAL again
	LDX #0
again:
	LDA org,X
	STA dst,X
	INX
	BNE again
.ENDMACRO
.REPEAT 16, REPCNT
	pagecpy GT_AURAM + $100 * REPCNT, AUROM + $100 * REPCNT
.ENDREPEAT
	LDA #1
	STA GT_AURESET
	LDA #$A8
	STA GT_AURATE

	LDA #<SONG
	STA PLAYHEAD
	LDA #>SONG
	STA PLAYHEAD+1

.MACRO inc16 mem
	INC mem
	BNE :+
	INC mem+1
:
.ENDMACRO

.MACRO dec16 mem
	; a little more trouble because we have to figure out wrap-around beforehand
	; which means we end up clobbering Y--better than A, I always say
	LDY #0
	CPY mem
	BNE :+
	DEC mem+1
:
	DEC mem
.ENDMACRO

	; the first u16 points to the const section, take that out now
	LDY #0
	LDA (PLAYHEAD),Y
	STA CONST
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA CONST+1
	inc16 PLAYHEAD

	; that's an offset, resolve it relative to the section
	CLC
	LDA #<SONG
	ADC CONST
	STA CONST
	LDA #>SONG
	ADC CONST+1
	STA CONST+1

	; we start waiting on ticks, so also load that value
	LDA (PLAYHEAD),Y
	STA TICKS
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA TICKS+1
	inc16 PLAYHEAD

	LDA #GT_DMAF_NMI
	STA GT_DMA
	; And now the NMI handler takes care of the rest
@ever:
	WAI
	BRA @ever

IRQ:
	; ack DMA, our only IRQ source
	STZ GT_DMAR_RUN
	RTI
NMI:
	; was it 0 when we got in here? some small intervals encode this way--do it immediately
	LDA TICKS
	ORA TICKS+1
	BEQ @pokes
	dec16 TICKS
	; hit deadline?
	LDA TICKS
	ORA TICKS+1
	BEQ @pokes
	RTI
@pokes:
	; PLAYHEAD points to our poke array, load the values from this poke, ADDR first
	LDY #0
	LDA (PLAYHEAD),Y
	STA ADDR
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA ADDR+1
	inc16 PLAYHEAD

	; if that's 0, we load ticks and wait instead
	LDA ADDR
	ORA ADDR+1
	BNE @one_poke

	LDA (PLAYHEAD),Y
	STA TICKS
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA TICKS+1
	inc16 PLAYHEAD

	; check to see if we're at the sentinel; we choose to loop here
	LDA TICKS
	AND TICKS+1
	CMP #$FF
	BEQ @restart
	RTI

@one_poke:
	LDA (PLAYHEAD),Y
	STA SIZE
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA OFFSET
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA OFFSET+1
	inc16 PLAYHEAD

	; add CONST to OFFSET--it's just easier this way
	CLC
	LDA CONST
	ADC OFFSET
	STA CADDR
	LDA CONST+1
	ADC OFFSET+1
	STA CADDR+1

	; do the copy
	LDY SIZE
@copy_loop:
	BEQ @pokes  ; zero bytes remain
	DEY  ; otherwise
	LDA (CADDR),Y
	STA (ADDR),Y
	TYA  ; set Z
	BRA @copy_loop

@restart:
	; all we'll do to loop is set the PLAYHEAD back to the beginning of the script
	; just like the RESET routine; this might leave some voices playing, oh well
	LDA #<SONG
	STA PLAYHEAD
	LDA #>SONG
	STA PLAYHEAD+1
	; skip const offset
	inc16 PLAYHEAD
	inc16 PLAYHEAD
	; get the next ticks
	LDY #0
	LDA (PLAYHEAD),Y
	STA TICKS
	inc16 PLAYHEAD
	LDA (PLAYHEAD),Y
	STA TICKS+1
	inc16 PLAYHEAD
	RTI

; TODO: this always needs to be in bank 127--it usually is, for long enough songs, but...
BANKED_RESET:
	; clear the screen blue as our first task, so we know we got here
	LDA #(GT_DMAF_ENABLE | GT_DMAF_COLFILL | GT_DMAF_IRQ | GT_DMAF_OPAQUE)
	STA GT_DMA
	cls (GT_HUE_BLUE | GT_SAT_FULL | $04)
	STZ GT_DMA

	; ensure we've banked in properly
	LDA #$07
	STA GT_VIA + VIA::DDRA
.MACRO sendbit bit
	LDA #(bit << 1)
	LDX #(bit << 1) | 1
	STA GT_VIA + VIA::XRA
	STX GT_VIA + VIA::XRA
	STA GT_VIA + VIA::XRA
.ENDMACRO
	sendbit 1  ; 7
	sendbit 1
	sendbit 1
	sendbit 1
	sendbit 1
	sendbit 1
	sendbit 1
	sendbit 0  ; 0
	LDA #$04
	STA GT_VIA + VIA::XRA
	STZ GT_VIA + VIA::XRA
	JMP RESET

.SEGMENT "VECTORS"
.ADDR NMI, BANKED_RESET, IRQ
