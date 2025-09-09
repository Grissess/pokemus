.SETCPU "W65C02"

ACC = $00
SCRATCH = $01
DAC = $8000

V_START = $10

.STRUCT VOICE
	PHASE .WORD
	PHVEL .WORD
	; since we have only 4k accessible address space, the top nibble is used for flags:
	; - $80: enable (must be set for the voice to contribute to DAC output and have phase updates)
	; - $40: "direct" (use phase instead of indexing a wavetable, address ignored--effectively a full-volume saw)
	; (rest reserved)
	TBL .ADDR
	; the actual pointer can be anywhere in ARAM, and should be [64]i8 offset from 0x80 output bias
	; since there's no volume control, you may want tables of various amplitudes
.ENDSTRUCT

.CODE
RESET:
	SEI
	CLD
	LDX #$FF
	TXS
	CLI

WAIT:
	WAI
	BRA WAIT

NMI:
	RTI

IRQ:
	LDA #$80
	STA ACC
	
.MACRO DOVOICE VN
.LOCAL V, SKIP, DIRECT
V = V_START + VN * .SIZEOF(VOICE)

	; do nothing if disabled
	BBR7 V + VOICE::TBL + 1, SKIP

	; phase velocity
	CLC
	LDA V + VOICE::PHASE
	ADC V + VOICE::PHVEL
	STA V + VOICE::PHASE
	LDA V + VOICE::PHASE + 1
	ADC V + VOICE::PHVEL + 1
	STA V + VOICE::PHASE + 1

	BBS6 V + VOICE::TBL + 1, DIRECT
	;BRA DIRECT

	; sampling case
	; 64-element wavetable demands we shift right 2x
	LSR A
	LSR A
	TAY
	LDA (V + VOICE::TBL),Y

DIRECT:

	; we now have A as a sample, but it's not scaled by volume--let's do that
;	BRA :++++++++
;	STA SCRATCH
;	LDA #0
;	CLC
;	BBR7 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR6 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR5 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR4 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR3 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR2 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR1 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:	LSR SCRATCH
;	BBR0 (V + VOICE::VOL),:+
;	ADC SCRATCH
;:
	; sample to ACC
	CLC
	ADC ACC
	STA ACC

SKIP:
.ENDMACRO

	DOVOICE 0
	DOVOICE 1
	DOVOICE 2
	DOVOICE 3
	DOVOICE 4
	DOVOICE 5

	LDA ACC
	STA DAC
	RTI

.SEGMENT "VECTORS"
.ADDR NMI, RESET, IRQ
