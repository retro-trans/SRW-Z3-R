"""Guarded NPJB00689 Unicode and proportional centering adapters."""
from rengoku_runtime import *

CENTER=0x149bc
CONVERTED=0x1499c
CONVERT=0x13b38
JOIN_TABLE=0x8ff200
JOIN_STATE=SCRATCH+0x40


def joined_data(codec):
    jp='エースボーナス'.encode('cp932')+b'\0';en=codec.encode('Ace Bonus')+b'\0'
    j=JOIN_TABLE+24;e=j+len(jp)
    return struct.pack('>6I',j,e,e,e,0,0)+jp+en


def joined_stub():
    # Match only the complete Ace Bonus heading, allowing the native typesetter's
    # bounded NUL gaps. Remember its range so subsequent pieces draw nothing.
    a=Asm();regs=(0,4,5,6,8,9,10,11,12)
    a.emit(dform(0xf8000001,1,1,-0x90))
    for i,r in enumerate(regs):a.emit(std(r,1,0x20+i*8))
    a.emit(0x7c000026);a.emit(std(0,1,0x68));a.emit(mr(8,3))
    address(a,10,JOIN_STATE);a.emit(lwz(11,10,0));a.emit(cmplw(8,11));a.br('beq','clear');a.br('blt','lookup')
    a.emit(lwz(12,10,4));a.emit(cmplw(8,12));a.br('bgt','lookup')
    a.emit(addi(3,10,8));a.br('b','done')
    a.label('clear');a.emit(addi(0,0,0));a.emit(stw(0,10,0));a.emit(stw(0,10,4))
    a.label('lookup');address(a,11,JOIN_TABLE)
    a.label('row');a.emit(lwz(6,11,0));a.emit(cmpwi(6,0));a.br('beq','done')
    a.emit(lhz(4,8,0));a.emit(lhz(9,6,0));a.emit(cmplw(4,9));a.br('bne','next')
    a.emit(mr(5,8));a.emit(addi(0,0,0))
    a.label('match');a.emit(lbz(9,6,0));a.emit(cmpwi(9,0));a.br('beq','hit')
    a.emit(lbz(4,5,0));a.emit(cmpwi(4,0));a.br('bne','byte')
    a.emit(addi(0,0,1));a.emit(cmpwi(0,8));a.br('bgt','next');a.emit(addi(5,5,1));a.br('b','match')
    a.label('byte');a.emit(cmplw(4,9));a.br('bne','next');a.emit(addi(0,0,0))
    a.emit(addi(5,5,1));a.emit(addi(6,6,1));a.br('b','match')
    a.label('next');a.emit(addi(11,11,8));a.br('b','row')
    a.label('hit');a.emit(lbz(4,5,0));a.emit(cmpwi(4,0));a.br('bne','next')
    a.emit(stw(8,10,0));a.emit(stw(5,10,4));a.emit(lwz(3,11,4))
    a.label('done');a.emit(ld(0,1,0x68));a.emit(0x7c0ff120)
    for i,r in enumerate(regs):a.emit(ld(r,1,0x20+i*8))
    a.emit(addi(1,1,0x90));a.emit(0x4e800020)
    return a.code()


def draw_entry(at,lookup,joined):
    a=Asm();a.emit(dform(0xf8000001,1,1,-0x60));a.emit(std(0,1,0x30))
    a.emit(0x7c0802a6);a.emit(std(0,1,0x20));a.emit(0x7c000026);a.emit(std(0,1,0x28))
    a.emit(std(3,1,0x38));a.emit(cmpwi(7,0));a.br('beq','done')
    a.emit(branch(at+len(a.words)*4,lookup,True))
    a.emit(ld(0,1,0x38));a.emit(cmplw(3,0));a.br('bne','done')
    a.emit(branch(at+len(a.words)*4,joined,True))
    a.label('done');a.emit(ld(0,1,0x20));a.emit(0x7c0803a6)
    a.emit(ld(0,1,0x28));a.emit(0x7c0ff120);a.emit(ld(0,1,0x30));a.emit(addi(1,1,0x60))
    a.emit(0x2f870000);a.emit(branch(at+len(a.words)*4,DRAW+4))
    return a.code()


def lookup_stub(table):
    a=Asm();regs=(0,4,5,6,8,9,10,11,12)
    a.emit(dform(0xf8000001,1,1,-0x90))
    for i,r in enumerate(regs):a.emit(std(r,1,0x20+i*8))
    a.emit(0x7c000026);a.emit(std(0,1,0x68))
    a.emit(mr(8,3));a.emit(lbz(0,8,0));a.emit(cmpwi(0,0));a.br('beq','done')
    a.emit(lbz(9,8,1));a.emit(dform(0x1c000000,0,0,256));a.emit(add(0,0,9))
    a.emit(dform(0x1c000000,0,0,4));address(a,11,table);a.emit(lwzx(11,11,0))
    a.emit(cmpwi(11,0));a.br('beq','done')
    a.label('entry');a.emit(lwz(12,11,0));a.emit(cmpwi(12,0));a.br('beq','done')
    a.emit(mr(5,8));a.emit(mr(6,12))
    a.label('compare');a.emit(lbz(9,5,0));a.emit(lbz(4,6,0));a.emit(cmplw(9,4));a.br('bne','next')
    a.emit(cmpwi(9,0));a.br('beq','found')
    a.emit(addi(5,5,1));a.emit(addi(6,6,1));a.br('b','compare')
    a.label('next');a.emit(addi(11,11,8));a.br('b','entry')
    a.label('found');a.emit(lwz(3,11,4))
    a.label('done');a.emit(ld(0,1,0x68));a.emit(0x7c0ff120)
    for i,r in enumerate(regs):a.emit(ld(r,1,0x20+i*8))
    a.emit(addi(1,1,0x90));a.emit(0x4e800020)
    return a.code()


def converted_stub(at,lookup):
    a=Asm();a.emit(lwz(30,2,-0x7f3c));a.emit(addi(3,30,0xb8))
    a.emit(branch(at+len(a.words)*4,lookup,True));a.emit(mr(31,3))
    a.emit(branch(at+len(a.words)*4,0x141a0))
    return a.code()


def center_stub(at,lookup):
    a=Asm();regs=(0,3,4,5,6,7,8,9,10,11,12);fps=tuple(range(14))
    a.emit(dform(0xf8000001,1,1,-0x180))
    for i,r in enumerate(regs):a.emit(std(r,1,0x30+i*8))
    a.emit(0x7c0802a6);a.emit(std(0,1,0x20));a.emit(0x7c000026);a.emit(std(0,1,0x28))
    for i,f in enumerate(fps):a.emit(dform(0xd8000000,f,1,0x90+i*8))
    a.emit(cmpwi(7,0));a.br('bne','cp932')
    a.emit(branch(at+len(a.words)*4,CONVERT,True))
    a.emit(lwz(9,2,-0x7f3c));a.emit(addi(3,9,0xb8))
    a.label('cp932');a.emit(branch(at+len(a.words)*4,lookup,True))
    a.emit(std(3,1,0x110));a.emit(mr(12,3));address(a,11,WIDTHS)
    a.emit(addi(0,0,0));a.emit(stw(0,1,0x120));a.emit(lfs(12,1,0x120))
    a.emit(addi(4,0,0));a.emit(addi(5,0,0))
    a.label('glyph');a.emit(lbz(9,12,0));a.emit(cmpwi(9,0));a.br('beq','done')
    a.emit(cmpwi(9,0x81));a.br('blt','fallback');a.emit(cmpwi(9,0x98));a.br('bgt','fallback')
    a.emit(lbz(0,12,1));a.emit(cmpwi(0,0x40));a.br('blt','fallback')
    a.emit(cmpwi(0,0xfc));a.br('bgt','fallback');a.emit(cmpwi(0,0x7f));a.br('beq','fallback')
    a.emit(addi(9,9,-0x81));a.emit(dform(0x1c000000,9,9,192));a.emit(add(9,9,0));a.emit(addi(9,9,-0x40))
    a.emit(cmpwi(9,FONT_CELLS));a.br('bge','fallback');a.emit(lbzx(10,11,9))
    a.emit(cmpwi(10,32));a.br('beq','style');a.emit(addi(5,0,1))
    a.label('style');a.emit(lwz(9,2,-0x7f3c));a.emit(lhz(0,9,0xac));a.emit(cmpwi(0,0));a.br('beq','normal')
    for flag,lo,hi in [(0xb1,0x8340,0x8491),(0xae,0x8260,0x8279),(0xb0,0x829f,0x82f1),(0xaf,0x8281,0x829a),(0xb2,0x8140,0x825f)]:
        label='skip%x'%flag;a.emit(lhz(0,12,0))
        a.emit(dform(0x28000000,0,0,lo));a.br('blt',label)
        a.emit(dform(0x28000000,0,0,hi));a.br('bgt',label)
        a.emit(lbz(0,9,flag));a.emit(cmpwi(0,0));a.br('bne','alternate');a.label(label)
    a.emit(addi(9,9,0x78));a.br('b','advance')
    a.label('alternate');a.emit(addi(9,9,0x88));a.br('b','advance')
    a.label('normal');a.emit(addi(9,9,0x54))
    a.label('advance');a.emit(cmpwi(10,32));a.br('beq','fullwidth')
    a.emit(std(10,1,0x120));a.emit(dform(0xc8000000,13,1,0x120))
    a.emit(0xfc00069c|(13<<21)|(13<<11));a.emit(0xfc000018|(13<<21)|(13<<11))
    a.emit(lfs(0,9,0));a.emit(fmuls(13,13,0))
    a.emit(lis(0,0x3d00));a.emit(stw(0,1,0x120));a.emit(lfs(0,1,0x120));a.emit(fmuls(13,13,0));a.br('b','sum')
    a.label('fullwidth');a.emit(lfs(13,9,8))
    a.label('sum');a.emit(fadds(12,12,13));a.emit(addi(12,12,2));a.emit(addi(4,4,1))
    a.emit(cmpwi(4,2048));a.br('bge','fallback');a.br('b','glyph')
    a.label('done');a.emit(cmpwi(5,0));a.br('beq','fallback')
    a.emit(lis(0,0x3f00));a.emit(stw(0,1,0x120));a.emit(lfs(0,1,0x120));a.emit(fmuls(12,12,0))
    a.emit(dform(0xc8000000,1,1,0x98));a.emit(0xec000028|(1<<21)|(1<<16)|(12<<11))
    def restore(success):
        for i,f in enumerate(fps):
            if not (success and f==1):a.emit(dform(0xc8000000,f,1,0x90+i*8))
        a.emit(ld(0,1,0x20));a.emit(0x7c0803a6)
        a.emit(ld(0,1,0x28));a.emit(0x7c0ff120)
        for i,r in enumerate(regs):
            if not (success and r in (3,7)):a.emit(ld(r,1,0x30+i*8))
        if success:a.emit(ld(3,1,0x110));a.emit(addi(7,0,1))
        a.emit(addi(1,1,0x180))
    restore(True);a.emit(branch(at+len(a.words)*4,DRAW))
    a.label('fallback');restore(False);a.emit(0xf821ff41);a.emit(branch(at+len(a.words)*4,CENTER+4))
    return a.code()
