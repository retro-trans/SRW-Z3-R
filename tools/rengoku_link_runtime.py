"""NPJB00689 link geometry, ported from Z3.1's measured-width approach.

Every address and live register below was checked in Rengoku's original ELF.
The main rectangle path uses a scene/glossary identity; the backlog path uses
a render-slot index. Neither is a character count. Speaker names have their
own widget. Original records, input navigation and draw/color tails stay native.
This module only generates bytes; build_game owns dry-run/output policy.
"""
import struct
from rengoku_runtime import (Asm, SCRATCH, TEXT, WIDTHS, FONT_CELLS, require,
    sha, branch, address, dform, addi, add, mr, lwz, lbz, lhz, ld, std,
    stw, lfs, stfs, lis, cmpwi, cmplw, fmuls)

LINK_WIDTHS = SCRATCH + 0x1000  # 256 float widths, separate from glyph widths
CAPTURE = 0x21a4cc
SELECT = 0x21412c
RECT_WIDTH = 0x2141c0
PRIMARY = 0x212244
PRIMARY_TAIL = 0x2121a4
SCENE_SITE = 0x21a4f4
COMPARE_SITE = 0x21a564
NAME_SITE = 0x2a7348
SCENE_MANAGER = 0x214eac
LINK_MANAGER = 0x21a0a0
GET_RECORD = 0x219e20
GET_SELECTION = 0x2a565c
GET_STYLE = 0x211fc0
STRLEN = 0x67d8cc
STRCMP = 0x682d58


def integer_float(a, reg, fp, slot=0xa0):
    a.emit(std(reg,1,slot));a.emit(dform(0xc8000000,fp,1,slot))
    a.emit(0xfc00069c|(fp<<21)|(fp<<11))
    a.emit(0xfc000018|(fp<<21)|(fp<<11))


def capture_stub():
    a=Asm();a.emit(dform(0x98000000,3,28,4))  # original length byte
    a.emit(lwz(9,1,0x70));a.emit(dform(0x1c000000,9,9,64))
    a.emit(lwz(0,1,0x74));a.emit(dform(0x1c000000,0,0,4));a.emit(add(9,9,0))
    address(a,10,LINK_WIDTHS);a.emit(add(10,10,9))
    address(a,9,SCRATCH);a.emit(lfs(13,9,0));a.emit(stfs(13,10,0))
    a.emit(0x4e800020)
    return a.code()


def select_stub():
    a=Asm();a.emit(mr(29,3))
    # The native getter preserves r4. Failed lookups never draw; bound the read.
    a.emit(0x5489063e);a.emit(dform(0x1c000000,9,9,4))  # clrlwi r9,r4,24
    address(a,10,LINK_WIDTHS);a.emit(add(9,9,10));a.emit(lfs(0,9,0))
    a.emit(stfs(0,1,0x88));a.emit(0x4e800020)
    return a.code()


def width_stub():
    a=Asm();a.emit(lfs(0,1,0x88));a.emit(stfs(0,31,8));a.emit(0x4e800020)
    return a.code()


def primary_stub(at):
    a=Asm()
    def call(target):a.emit(branch(at+len(a.words)*4,target,True))
    # Rengoku keeps the style/draw context in r28, not Z3.1's r27.
    # r27 is dead here and available as the slot counter. r29 may be reused.
    call(SCENE_MANAGER);a.emit(lwz(9,3,12));a.emit(stw(9,1,0x70))
    a.emit(cmpwi(9,0));a.br('beq','done')
    a.emit(mr(3,31));call(GET_SELECTION);a.emit(stw(3,1,0x74))
    call(LINK_MANAGER);a.emit(mr(29,3));a.emit(addi(27,0,0))
    a.label('loop');a.emit(mr(3,29));a.emit(mr(4,27));call(GET_RECORD)
    a.emit(cmpwi(3,0));a.br('beq','next')
    a.emit(lwz(9,3,12));a.emit(lwz(10,1,0x70));a.emit(cmplw(9,10));a.br('bne','next')
    a.emit(lwz(9,3,16));a.emit(lwz(10,1,0x74));a.emit(cmplw(9,10));a.br('beq','found')
    a.label('next');a.emit(addi(27,27,1));a.emit(cmpwi(27,256));a.br('blt','loop');a.br('b','done')
    a.label('found');a.emit(stw(3,1,0x78));address(a,9,LINK_WIDTHS)
    a.emit(dform(0x1c000000,10,27,4));a.emit(add(9,9,10))
    a.emit(lfs(0,9,0));a.emit(stfs(0,1,0x7c))
    a.emit(mr(3,31));a.emit(mr(4,28));call(GET_STYLE)
    a.emit(lbz(9,3,0x2d));a.emit(0x7c000774|(9<<21)|(9<<16));a.emit(addi(9,9,1))
    a.emit(lwz(11,1,0x78));a.emit(lhz(10,11,2))
    a.emit(0x7c000734|(10<<21)|(10<<16));a.emit(addi(10,10,1))
    a.emit(lhz(11,11,0));a.emit(0x7c000734|(11<<21)|(11<<16))
    for reg,offset in ((11,0),(10,4),(9,12)):
        integer_float(a,reg,0);a.emit(stfs(0,30,offset))
    a.emit(lfs(0,1,0x7c));a.emit(stfs(0,30,8))
    a.label('done');a.emit(branch(at+len(a.words)*4,PRIMARY_TAIL))
    return a.code()


def scene_stub(at):
    a=Asm();a.emit(lwz(3,3,4));a.emit(cmpwi(3,0));a.br('bne','done')
    # Preserve the backlog's explicit context; dialogue uses scene zero.
    a.emit(dform(0xf8000001,1,1,-0x70));a.emit(0x7c0802a6);a.emit(std(0,1,0x80))
    a.emit(branch(at+len(a.words)*4,SCENE_MANAGER,True));a.emit(lwz(3,3,12))
    a.emit(ld(0,1,0x80));a.emit(0x7c0803a6);a.emit(addi(1,1,0x70))
    a.label('done');a.emit(0x4e800020)
    return a.code()


def compare_stub(at,lookup):
    # Compare the displayed forms on both sides. Unknown Japanese still takes
    # native strcmp, and already-encoded English is unchanged by exact lookup.
    a=Asm();a.emit(dform(0xf8000001,1,1,-0x80))
    a.emit(0x7c0802a6);a.emit(std(0,1,0x90))
    a.emit(branch(at+len(a.words)*4,lookup,True));a.emit(std(3,1,0x70))
    a.emit(mr(3,4));a.emit(branch(at+len(a.words)*4,lookup,True));a.emit(mr(4,3))
    a.emit(ld(3,1,0x70));a.emit(ld(0,1,0x90));a.emit(0x7c0803a6)
    a.emit(addi(1,1,0x80));a.emit(branch(at+len(a.words)*4,STRCMP))
    return a.code()


def name_stub(at,lookup):
    # Enter by B: the native widget has already saved LR. Return width bits
    # through r3, then retain the native rectangle's coordinates and height.
    a=Asm();a.emit(branch(at,lookup,True));a.emit(stw(3,1,0x70))
    a.emit(mr(4,3));a.emit(addi(8,0,0));address(a,5,WIDTHS)
    a.label('loop');a.emit(lbz(6,4,0));a.emit(cmpwi(6,0));a.br('beq','measured')
    a.emit(addi(6,6,-0x81));a.emit(dform(0x28000000,0,6,0x17));a.br('bgt','fallback')
    a.emit(lbz(7,4,1));a.emit(cmpwi(7,0x7f));a.br('beq','fallback')
    a.emit(addi(7,7,-0x40));a.emit(dform(0x28000000,0,7,0xbc));a.br('bgt','fallback')
    a.emit(dform(0x1c000000,6,6,192));a.emit(add(6,6,7))
    a.emit(dform(0x28000000,0,6,FONT_CELLS-1));a.br('bgt','fallback')
    a.emit(0x7c0000ae|(6<<21)|(5<<16)|(6<<11))  # lbzx r6,r5,r6
    a.emit(cmpwi(6,32));a.br('beq','fallback')
    a.emit(add(8,8,6));a.emit(addi(4,4,2));a.br('b','loop')
    a.label('measured');a.emit(lwz(9,31,0xc))
    a.emit(0x7c0001d6|(8<<21)|(8<<16)|(9<<11));a.emit(lis(9,0x3d00));a.br('b','float')
    a.label('fallback');a.emit(lwz(3,1,0x70))
    a.emit(branch(at+len(a.words)*4,STRLEN,True))
    a.emit(0x5468f87e);a.emit(lwz(9,31,0x14))  # srwi r8,r3,1
    a.emit(0x7c0001d6|(8<<21)|(8<<16)|(9<<11));a.emit(lis(9,0x3f80))
    a.label('float');integer_float(a,8,0,0x70)
    a.emit(stw(9,1,0x70));a.emit(lfs(10,1,0x70));a.emit(fmuls(0,0,10))
    a.emit(stfs(0,1,0x70));a.emit(lwz(3,1,0x70))
    a.emit(branch(at+len(a.words)*4,0x2a7350))
    return a.code()


def generators():
    return [
        ('link_capture',lambda at,s:capture_stub()),
        ('link_select',lambda at,s:select_stub()),
        ('link_width',lambda at,s:width_stub()),
        ('link_primary',lambda at,s:primary_stub(at)),
        ('link_scene',lambda at,s:scene_stub(at)),
        ('link_compare',lambda at,s:compare_stub(at,s['lookup'])),
        ('link_name',lambda at,s:name_stub(at,s['lookup']))]


def edits(stubs):
    result=[]
    for site,old,name,link in [
        (CAPTURE,0x987c0004,'link_capture',True),
        (SELECT,0x7c7d1b78,'link_select',True),
        (RECT_WIDTH,0xd01f0008,'link_width',True),
        (PRIMARY,branch(PRIMARY,SCENE_MANAGER,True),'link_primary',False),
        (SCENE_SITE,branch(SCENE_SITE,0x20fb74,True),'link_scene',True),
        (COMPARE_SITE,branch(COMPARE_SITE,STRCMP,True),'link_compare',True),
        (NAME_SITE,branch(NAME_SITE,STRLEN,True),'link_name',False)]:
        result.append((site,old,branch(site,stubs[name],link),name))
    # The name helper returns an IEEE float, so bypass native integer scaling.
    for site,old,new in [(0x2a7358,0x5463f87e,0x60000000),
                         (0x2a7374,0x7c6349d6,0x60000000),
                         (0x2a7380,0xf8610070,stw(3,1,0x70)),
                         (0x2a7384,0xc9410070,lfs(0,1,0x70)),
                         (0x2a7388,0xfd40569c,0x60000000),
                         (0x2a738c,0xfc005018,0x60000000)]:
        result.append((site,old,new,'link name float width'))
    return result


def guard(original):
    require(SCRATCH+0x48<LINK_WIDTHS and LINK_WIDTHS+1024<TEXT,'Link width cache overlaps owned storage')
    # Complete native blocks cover allocation, live registers, style access,
    # active-record checks and stack scratch (secondary +88; primary +a0).
    blocks = [
        (0x212244,0x212340,'aae7214aeb0582dc356388b6a6a4ffcd100d313d9633f761b70f7f67f5de661c'),
        (0x213f94,0x2141c8,'eb48d607183b5237daa4895bedce7baf10da40084a7cbaf4a6ca703e7b69335b'),
        (0x21a3d8,0x21a624,'8810c5bbd1eefc1588d42b932954e7db5b5547e157e90c0c99e71dd8fc6a0e83'),
        (0x2a727c,0x2a73ac,'5acb877f412126cea92379e4e3187f2377e271a035fbd47734b9a7f736b0b1fa'),
        (0x219e20,0x219e9c,'70975b4870c1188b0b0e811c36d96d37c2f5517127eb181dbde7a3759029e38f'),
        (0x2149f0,0x214a18,'70c83c563ba15494e61dfbc64f4c1b75008a0829b2dfc6febde19201376e0f8f')]
    for lo,hi,digest in blocks:
        require(sha(original[lo-0x10000:hi-0x10000])==digest,'Link source block '+hex(lo))
    for site,target in [(0x21e5b0,0x21d9cc),(0x21e5e8,0x21a3d8),
                        (0x21a4c4,STRLEN),(0x214120,GET_RECORD)]:
        require(struct.unpack_from('>I',original,site-0x10000)[0]==branch(site,target,True),'Link call guard '+hex(site))
    require(original[0x1ffb74:0x1ffb7c]==bytes.fromhex('806300044e800020'),'Scene getter changed')
    require(original[0x29565c:0x295668]==bytes.fromhex('81230004886900034e800020'),'Selected glossary getter changed')
