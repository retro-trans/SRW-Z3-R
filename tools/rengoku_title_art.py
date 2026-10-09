"""English Rengoku title sprites; preserve native Z, menu and animation bytes.

The source is independently located through ScAnime_Z3TITLE_2D = 132 and
the corresponding EFF member 133. Preview-only by default; --write saves
inspection copies to a fresh work directory. No original assets are written.
"""
import argparse
import json
import struct
from pathlib import Path

from PIL import Image
from cpk import CPK
from rengoku_runtime import require, sha

ROOT = Path(__file__).resolve().parents[1]
EFF = 'USRDIR/DATA_REN/ANIME/EFFPS3.CPK'
MEMBER, GTF = 133, 0xecfe0
SIZE = (1024, 720)
SOURCE_SHA = 'e13739e4e1b893bb2dcd1eaddf3c15921b6d0d7efed6e9173c2d8c335460f95a'
ROWS = ((0, 0, 706, 296, 'wordmark'), (0, 603, 339, 117, 'subtitle'))
# Every distinct Rengoku Z sample, including its one-frame transition fill.
Z_BOXES = ((24, 304, 473, 601), (664, 268, 1024, 550),
           (666, 268, 1024, 564), (665, 268, 1024, 557))
SAMPLES = ((1, 0, 0, 706, 296, 0x5800, 1721),
           (0, 0, 603, 339, 117, 0x5000, 1672),
           (0, 24, 304, 449, 297, 0x5000, 1622),
           (1, 24, 304, 449, 297, 0x5000, 10),
           (0, 664, 268, 360, 282, 0x5800, 1100),
           (0, 666, 268, 358, 296, 0x5800, 1062),
           (0, 665, 268, 359, 289, 0x5800, 2))


def config():
    meta = json.loads((ROOT / 'localization/title_screen.json').read_text(encoding='utf8'))
    require(meta['schema'] == 1 and meta['asset'] == EFF + ':133' and
            meta['source_sha256'] == SOURCE_SHA, 'Title source binding changed')
    require(meta['display'] == ['3rd SUPER ROBOT WARS', 'PURGATORY', 'CHAPTER'],
            'Title text changed; regenerate and inspect matching sprites')
    return meta


def span(raw):
    require(raw[GTF:GTF + 4] == b'\x02\x02\0\0' and
            struct.unpack_from('>I', raw, GTF + 8)[0] == 9, 'Title GTF header')
    p = GTF + 12 + 36
    offset, size = struct.unpack_from('>II', raw, p + 4)
    require(raw[p + 12] == 0xa5 and struct.unpack_from('>HH', raw, p + 20) == SIZE,
            'Title must use its own linear ARGB32 atlas')
    require(size == SIZE[0] * SIZE[1] * 4 and GTF + offset + size <= len(raw),
            'Title texture bounds')
    return GTF + offset


def atlas(raw):
    p = span(raw)
    return Image.frombytes('RGBA', SIZE, raw[p:p + SIZE[0] * SIZE[1] * 4], 'raw', 'ARGB')


def audit(raw):
    require(sha(raw) == SOURCE_SHA, 'Rengoku title resource changed')
    span(raw)
    for *rect, count in SAMPLES:
        pattern = struct.pack('>6H', *rect) + b'\x01\x01\0\x01'
        require(raw[:GTF].count(pattern) == count, 'Rengoku title animation/sample drift')


def tiles():
    meta = config()
    for x, y, w, h, key in ROWS:
        data = (ROOT / meta[key]['path']).read_bytes()
        require(sha(data) == meta[key]['sha256'], 'Title sprite not inspected: ' + key)
        with Image.open(ROOT / meta[key]['path']) as im:
            require(im.mode == 'RGBA' and im.size == (w, h) and
                    im.getchannel('A').getextrema() == (0, 255), 'Title sprite dimensions/alpha')
            yield (x, y, w, h), im.copy()


def apply(raw):
    audit(raw)
    before = atlas(raw)
    im = before.copy()
    for (x, y, w, h), tile in tiles():
        old = before.crop((x, y, x + w, y + h))
        # Keep the native RGBA values when BOTH pixels are transparent.
        # A native fiery-Z UV intersects transparent wordmark padding.
        tile.putdata([new if new[3] or previous[3] else previous
                      for previous, new in zip(old.getdata(), tile.getdata())])
        im.paste(tile, (x, y))
    for box in Z_BOXES:
        require(im.crop(box).tobytes() == before.crop(box).tobytes(), 'Native Z sprite changed')
    r, g, b, a = im.split()
    pixels = Image.merge('RGBA', (a, r, g, b)).tobytes()
    out = bytearray(raw); start = span(raw)
    out[start:start + len(pixels)] = pixels
    return bytes(out)


def verify(raw, built):
    require(len(raw) == len(built) and raw != built, 'Title insertion missing/size changed')
    require(built == apply(raw), 'Title art differs from inspected sprites')
    restored = bytearray(built); start = span(raw)
    for x, y, w, h, _ in ROWS:
        for yy in range(y, y + h):
            p = start + (yy * SIZE[0] + x) * 4
            restored[p:p + w * 4] = raw[p:p + w * 4]
    require(bytes(restored) == raw, 'Unrelated title pixels/geometry/animation changed')


def prepare(asset):
    raw = asset('work/pkg/' + EFF + ':' + str(MEMBER)); built = apply(raw)
    verify(raw, built)
    return {(EFF, MEMBER): built}, {
        'asset': EFF + ':' + str(MEMBER), 'source_sha256': sha(raw),
        'output_sha256': sha(built), 'display': config()['display'],
        'wordmark_animation_samples': 1721, 'subtitle_animation_samples': 1672,
        'native_z_and_unrelated_bytes_preserved': True,
        'sprites': {key: config()[key] for *_, key in ROWS}}


def composition(raw, menu=False):
    """Sprite fit proof using observed settled quads; not a gameplay capture."""
    im = atlas(raw)
    if menu:
        rows = (((664, 268, 1024, 550), (225, -227, 441, -57)),
                ((24, 304, 473, 601), (204, -225, 474, -47)),
                ((0, 0, 706, 296), (-153, -232, 306, -40)),
                ((0, 603, 339, 720), (-19, -77, 201, -1)))
    else:
        rows = (((666, 268, 1024, 564), (88, -192, 411, 74)),
                ((24, 304, 473, 601), (54, -189, 458, 78)),
                ((0, 0, 706, 296), (-435, -181, 200, 85)),
                ((0, 603, 339, 720), (-251, 33, 55, 138)))
    left = min(q[0] for _, q in rows); top = min(q[1] for _, q in rows)
    right = max(q[2] for _, q in rows); bottom = max(q[3] for _, q in rows)
    proof = Image.new('RGBA', (right - left + 24, bottom - top + 24), (12, 29, 27, 255))
    for box, (x0, y0, x1, y1) in rows:
        tile = im.crop(box).resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
        proof.alpha_composite(tile, (12 + x0 - left, 12 + y0 - top))
    return proof


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--out', type=Path, default=ROOT / 'work/title010_preview')
    args = ap.parse_args(); out = args.out.resolve()
    require(ROOT / 'work' in out.parents and not out.exists(), 'Use a fresh work preview directory')
    cpk = CPK(str(ROOT / 'work/pkg' / EFF))
    raw = cpk.read(next(e for e in cpk.files if e['id'] == MEMBER)); built = apply(raw)
    verify(raw, built)
    print('Rengoku EFF 133: two English title sprites, 3393 native references; Z and all unrelated bytes preserved.')
    print('Source SHA256:', sha(raw)); print('Output SHA256:', sha(built))
    for rect, tile in tiles(): print('Sprite', rect, 'alpha bounds', tile.getchannel('A').getbbox())
    print('Preview output:', out)
    if not args.write:
        print('DRY RUN; --write saves new atlas and large/menu sprite-fit proofs.'); return
    out.mkdir(parents=True)
    atlas(built).save(out / 'title_atlas.png')
    composition(built).save(out / 'title_large.png')
    composition(built, True).save(out / 'title_menu.png')


if __name__ == '__main__':
    main()
