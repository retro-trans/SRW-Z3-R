"""Translate generated gold rewards after native composition, in owned storage."""
from rengoku_runtime import (SCRATCH,require,addi,lbz,lhz,cmpwi,mr,address,
                             dform,add)

TABLE=0x8ff300
BUFFER=SCRATCH+0x200
CAPACITY=128
PREFIX='金塊　'.encode('cp932')

def guard(original):
    require(original[0x95f34c:0x95f34c+7]==PREFIX+b'\0','Rengoku gold label changed')
    require(BUFFER+CAPACITY<SCRATCH+0x1000,'Gold scratch overlaps link cache')

def data(codec):
    full=codec.encode('Gold Bar ');short=codec.encode('Gold ')
    require(len(full)<24 and len(short)<32,'Gold prefix table overflow')
    return (PREFIX+b'\0').ljust(8,b'\0')+(full+b'\0').ljust(24,b'\0')+(short+b'\0').ljust(32,b'\0')+b''.join(codec.encode(str(i)) for i in range(10))

def emit(a,table):
    # Called inline on exact-lookup miss, with original input in r3/r8.
    # Use only registers already saved by lookup_stub; r7 and LR stay intact.
    for i,value in enumerate(PREFIX):
        a.emit(lbz(10,8,i));a.emit(cmpwi(10,value));a.br('bne','done')
    a.emit(addi(4,8,len(PREFIX)));a.emit(addi(6,0,0));a.emit(addi(12,0,64))
    a.label('gold_validate')
    a.emit(cmpwi(12,0));a.br('beq','done');a.emit(addi(12,12,-1))
    a.emit(lbz(10,4,0));a.emit(cmpwi(10,0));a.br('beq','gold_valid')
    a.emit(cmpwi(10,32));a.br('beq','gold_space')
    a.emit(cmpwi(10,0x81));a.br('beq','gold_wide_space')
    a.emit(cmpwi(10,0x82));a.br('beq','gold_wide_digit')
    a.emit(cmpwi(10,48));a.br('blt','done');a.emit(cmpwi(10,57));a.br('bgt','done')
    a.emit(addi(4,4,1));a.br('b','gold_digit_valid')
    a.label('gold_wide_digit');a.emit(lbz(10,4,1))
    a.emit(cmpwi(10,0x4f));a.br('blt','done');a.emit(cmpwi(10,0x58));a.br('bgt','done')
    a.emit(addi(4,4,2))
    a.label('gold_digit_valid');a.emit(addi(6,6,1));a.emit(cmpwi(6,10));a.br('bgt','done')
    a.br('b','gold_validate')
    a.label('gold_wide_space');a.emit(lbz(10,4,1));a.emit(cmpwi(10,0x40));a.br('bne','done')
    a.emit(addi(4,4,1))
    a.label('gold_space');a.emit(addi(4,4,1));a.br('b','gold_validate')
    a.label('gold_valid')
    address(a,9,table+8);a.emit(cmpwi(6,0));a.br('beq','gold_compact')
    a.emit(cmpwi(6,8));a.br('bgt','gold_compact');a.br('b','gold_prefix')
    a.label('gold_compact');address(a,9,table+32)
    a.label('gold_prefix');address(a,5,BUFFER)
    a.label('gold_copy_prefix');a.emit(lbz(10,9,0));a.emit(cmpwi(10,0));a.br('beq','gold_amount')
    a.emit(dform(0x98000000,10,5,0));a.emit(addi(5,5,1));a.emit(addi(9,9,1));a.br('b','gold_copy_prefix')
    a.label('gold_amount');a.emit(addi(4,8,len(PREFIX)));address(a,11,table+64)
    a.label('gold_emit_digit');a.emit(lbz(10,4,0));a.emit(cmpwi(10,0));a.br('beq','gold_finish')
    a.emit(cmpwi(10,32));a.br('beq','gold_skip_space')
    a.emit(cmpwi(10,0x81));a.br('beq','gold_skip_wide_space')
    a.emit(cmpwi(10,0x82));a.br('beq','gold_emit_wide_digit')
    a.emit(addi(0,10,-48));a.emit(addi(4,4,1));a.br('b','gold_store_digit')
    a.label('gold_emit_wide_digit');a.emit(lbz(10,4,1));a.emit(addi(0,10,-0x4f));a.emit(addi(4,4,2))
    a.label('gold_store_digit');a.emit(add(0,0,0));a.emit(add(9,11,0));a.emit(lhz(12,9,0))
    a.emit(dform(0xb0000000,12,5,0));a.emit(addi(5,5,2));a.br('b','gold_emit_digit')
    a.label('gold_skip_wide_space');a.emit(addi(4,4,1))
    a.label('gold_skip_space');a.emit(addi(4,4,1));a.br('b','gold_emit_digit')
    a.label('gold_finish');a.emit(addi(0,0,0));a.emit(dform(0x98000000,0,5,0));address(a,3,BUFFER)
