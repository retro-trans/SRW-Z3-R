"""Keep the Rengoku Combo popup legible at every map zoom.

The original caller multiplies the animated scale by map zoom; the shared
quad drawer then multiplies by map zoom again. State 0x35 selects texture 6
of TPACK member 2, the native Combo +1/+2/+3/+4/MAX strip. Change only that
state to a 64-world-unit quad (one tile), retaining animation and centering.
This module emits code in memory; it never writes source assets.
"""
import struct

from rengoku_runtime import (Asm, require, dform, std, ld, lbz, cmpwi,
                             lis, ori, stw, lfs, fmuls, addi, branch)

SITE = 0x3a46b4
ORIGINAL = 0xec9e07f2  # fmuls f4,f30,f31: map zoom * animated popup scale
STATE = 0x35
SCALE = 0.8  # native 80-unit quad * 0.8 = one 64-unit map tile
SIGNATURES = {
    0x3a4640: 'c3ff0010c3ca306cfda00018fc004018',
    # Select texture 6 for state 0x35, texture 5 otherwise; pass the same
    # native frame index, alpha, center and depth into the shared renderer.
    0x3a4688: ('889c00308062f69c6884003538c000007c8400d054840ffe20840006'
               '7c8407b47c8523784bc7818160000000ec9e07f2a11f0016a0df0014'
               '38e000007d080734c062f6a07cc60734c02100b4c04100b04bffc76d60000000'),
    0x3a0ef0: 'c00b306cec000372',  # shared half-size = zoom * 40
    0x3a0f24: 'ec0007327d094378ed2c582aeda0f82aefff0028ed40f02aefde0028',
    0x3a4fb8: '38e00035a3dc0032a3fc003498fc00304bffe6e4',
}


def guard(original):
    for address, expected in SIGNATURES.items():
        value = bytes.fromhex(expected)
        require(original[address - 0x10000:address - 0x10000 + len(value)] == value,
                'Rengoku Combo consumer changed: ' + hex(address))
    require(original[0x943568:0x943570] == struct.pack('>ff', 40., 80.),
            'Rengoku map sprite half-size or UV stride changed')


def stub(at):
    a = Asm()
    a.emit(dform(0xf8000001, 1, 1, -0x50))
    a.emit(std(0, 1, 0x20)); a.emit(std(12, 1, 0x28))
    a.emit(0x7c000026); a.emit(std(0, 1, 0x30))  # preserve CR
    a.emit(lbz(12, 28, 0x30)); a.emit(cmpwi(12, STATE))
    a.br('bne', 'original')
    value = struct.unpack('>I', struct.pack('>f', SCALE))[0]
    a.emit(lis(12, value >> 16)); a.emit(ori(12, 12, value & 0xffff))
    a.emit(stw(12, 1, 0x38)); a.emit(lfs(4, 1, 0x38))
    a.emit(fmuls(4, 31, 4)); a.br('b', 'restore')
    a.label('original'); a.emit(ORIGINAL)
    a.label('restore'); a.emit(ld(0, 1, 0x30)); a.emit(0x7c0ff120)
    a.emit(ld(12, 1, 0x28)); a.emit(ld(0, 1, 0x20))
    a.emit(addi(1, 1, 0x50))
    a.emit(branch(at + len(a.words) * 4, SITE + 4))
    return a.code()


def report():
    return {'state': hex(STATE), 'site': hex(SITE),
            'source': 'TPACKPS3.CPK member 2 texture 6, five native Combo frames',
            'old_quad_world_units': '80 * map_zoom * animation_scale',
            'new_quad_world_units': '64 * animation_scale',
            'screen_zoom_applied_once': True,
            'native_sprite_frames_and_timing_preserved': True,
            'other_popup_states_preserved': True,
            'gameplay_tested': False}
