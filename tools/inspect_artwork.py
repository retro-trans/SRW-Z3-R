"""Render original artwork for inspection; never edit or overwrite game assets."""
import argparse
import io
import json
import struct
import re
from pathlib import Path
from PIL import Image
from cpk import CPK
from non_dialogue import ROOT, encoded, digest


def unswizzle(data, width, height, bpp):
    output = bytearray(width*height*bpp)
    wx, hy = (width-1).bit_length(), (height-1).bit_length()
    for y in range(height):
        for x in range(width):
            n, bit = 0, 0
            for i in range(max(wx, hy)):
                if i < wx:
                    n |= ((x >> i) & 1) << bit
                    bit += 1
                if i < hy:
                    n |= ((y >> i) & 1) << bit
                    bit += 1
            dest = (y*width+x)*bpp
            output[dest:dest+bpp] = data[n*bpp:n*bpp+bpp]
    return bytes(output)


def textures(raw):
    if raw[:3] not in (b'\x02\x02\x00', b'\x01\x05\x00'):
        return
    count = struct.unpack_from('>I', raw, 8)[0]
    if not 0 < count < 100:
        raise ValueError('Invalid texture count')
    for i in range(count):
        pos = 12+i*36
        _, offset, size = struct.unpack_from('>III', raw, pos)
        fmt = raw[pos+12]
        width, height = struct.unpack_from('>HH', raw, pos+20)
        bpp = 2 if fmt & 0x9f == 0x8b else 4
        if not offset <= offset+size <= len(raw):
            raise ValueError('Texture extent invalid')
        if size != width*height*bpp:
            raise ValueError('Unimplemented texture layout')
        # Some animation resources have one descriptor and consecutive frames.
        frames = (len(raw)-offset)//size if count == 1 and (len(raw)-offset)%size == 0 else 1
        for frame in range(frames):
            data = raw[offset+frame*size:offset+(frame+1)*size]
            if not fmt & 0x20:
                data = unswizzle(data, width, height, bpp)
            if bpp == 4:
                image = Image.frombytes('RGBA', (width, height), data, 'raw', 'ARGB')
            else:
                gray = bytes(max(data[x] >> 4, data[x] & 15, data[x+1] >> 4, data[x+1] & 15)*17 for x in range(0, len(data), 2))
                image = Image.frombytes('L', (width, height), gray)
            yield i, frame, image


def texture_blocks(raw):
    """Find bounded GTF blocks, including concatenated and wrapped resources."""
    covered = 0
    for match in re.finditer(rb'(?:\x02\x02\x00|\x01\x05\x00)', raw):
        start = match.start()
        if start < covered or start+48 > len(raw):
            continue
        count = struct.unpack_from('>I', raw, start+8)[0]
        if not 0 < count < 100 or start+12+36*count > len(raw):
            continue
        ends = []
        for i in range(count):
            pos = start+12+36*i
            _, off, size = struct.unpack_from('>III', raw, pos)
            if off < 12+36*count or start+off+size > len(raw):
                break
            ends.append(off+size)
        if len(ends) != count:
            continue
        covered = start+max(ends)
        yield start, raw[start:covered]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('family', choices=('manual', 'aid', 'kdata', 'tpack', 'tpack_extra', 'battle_ui'))
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    output = ROOT / 'work/artwork' / args.family
    if args.family == 'manual':
        inputs = sorted((ROOT / 'work/pkg/MANUAL').glob('*.DDS')) + [ROOT / 'work/pkg/ICON0.PNG', ROOT / 'work/pkg/PIC1.PNG']
        records = [(p.stem, p.read_bytes(), str(p.relative_to(ROOT))) for p in inputs] if args.write else [(p.stem, None, str(p.relative_to(ROOT))) for p in inputs]
    else:
        paths = {'aid': 'AIDDATA/AIDDATAPACK_R.CPK', 'kdata': 'KURODATA/KDATAPS3Z3REN.CPK', 'tpack': 'TABATA/TPACKPS3.CPK', 'tpack_extra': 'TABATA/TPACKPS3.CPK', 'battle_ui': 'BATTLE/CMN.CPK'}
        path = ROOT / 'work/pkg/USRDIR/DATA_REN' / paths[args.family]
        if args.family == 'battle_ui':
            path = next((ROOT / 'work/pkg').rglob('CMN.CPK'))
        cpk = CPK(str(path))
        ids = {'aid': [1, 2, 3, 7, 8, 9, 10, 11, 12], 'kdata': [0, 1, 2, 3], 'tpack': list(range(19)), 'tpack_extra': [0], 'battle_ui': [e['id'] for e in cpk.files]}[args.family]
        records = [(str(e['id']), cpk.read(e) if args.write else None, path.relative_to(ROOT).as_posix()+':'+str(e['id'])) for e in cpk.files if e['id'] in ids]
        if args.family == 'battle_ui':
            path = next((ROOT / 'work/pkg').rglob('BAR.CPK'))
            cpk = CPK(str(path))
            records.extend(('bar'+str(e['id']), cpk.read(e) if args.write else None, path.relative_to(ROOT).as_posix()+':'+str(e['id'])) for e in cpk.files)
    if not args.write:
        print('New inspection directory:', output)
        for stem, _, asset in records:
            print(asset, '->', stem+'_texture_frame.png')
        print('DRY RUN; --write extracts and renders copies.')
        return
    if output.exists():
        raise ValueError('Refusing existing inspection directory')
    output.mkdir(parents=True)
    manifest = []
    for stem, raw, asset in records:
        if raw.startswith((b'\x89PNG', b'DDS ')):
            images = [(0, 0, Image.open(io.BytesIO(raw)))]
        else:
            if args.family in ('tpack_extra', 'battle_ui'):
                images = ((str(base)+'-'+str(tex), frame, image) for base, block in texture_blocks(raw) for tex, frame, image in textures(block))
            else:
                images = textures(raw)
        for tex, frame, image in images:
            target = output / (stem+'_'+str(tex)+'_'+str(frame)+'.png')
            image.save(target)
            manifest.append({'asset': asset, 'sha256': digest(raw), 'texture': tex, 'frame': frame, 'image': target.relative_to(ROOT).as_posix(), 'size': list(image.size)})
            print(target.name, image.size, flush=True)
    (output / 'manifest.json').write_text(encoded(manifest), encoding='utf-8')


if __name__ == '__main__':
    main()
