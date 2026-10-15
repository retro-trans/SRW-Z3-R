"""Version/Retro Trans credit on Rengoku's own press-any-button background.

Matches the sibling's two-line placement and font recipe, using NPJB00689
EFF member 133 texture 0 and its independently checked GTF/source identity.
Never applies sibling executable addresses, animation offsets or background.
"""
import argparse
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from cpk import CPK
import build_version
import rengoku_title_art as title
from rengoku_runtime import DEFAULT_FONT, require, sha

ROOT = Path(__file__).resolve().parents[1]
EFF, MEMBER, GTF = title.EFF, title.MEMBER, title.GTF
TEXTURE, SIZE = 0, (1280, 720)
BOX, FONT_SIZE = (912, 640, 1252, 696), 18
CREDIT = 'github.com/retro-trans'
BACKGROUND_SHA = '9e0f3820a99d54df08ddba114f4c341eba1868c2793c745da6d7911a11b12b4c'


def texture_span(raw):
    require(raw[GTF:GTF+4] == b'\x02\x02\0\0' and struct.unpack_from('>I', raw, GTF+8)[0] == 9,
            'Rengoku title GTF identity changed')
    p = GTF + 12 + TEXTURE * 36
    offset, size = struct.unpack_from('>II', raw, p+4)
    require(raw[p+12] == 0xa5 and struct.unpack_from('>HH', raw, p+20) == SIZE,
            'Rengoku title background must be linear ARGB32 at 1280x720')
    require(size == SIZE[0]*SIZE[1]*4 and GTF+offset+size <= len(raw), 'Title background bounds')
    return GTF+offset, size


def background(raw):
    p, size = texture_span(raw)
    return Image.frombytes('RGBA', SIZE, raw[p:p+size], 'raw', 'ARGB')


def overlay(font, version):
    build_version.version_key(version)
    scale = 4
    width, height = BOX[2]-BOX[0], BOX[3]-BOX[1]
    canvas = Image.new('RGBA', (width*scale, height*scale))
    face = ImageFont.truetype(str(font), FONT_SIZE*scale)
    for text, bottom in (('v'+version, 26), (CREDIT, height)):
        l, t, r, b = face.getbbox(text, stroke_width=scale)
        require(r-l < (width-4)*scale and b-t <= 24*scale, 'Title footer would clip or overlap')
        ink = Image.new('RGBA', (r-l, b-t))
        ImageDraw.Draw(ink).text((-l, -t), text, font=face, fill=(240,246,255,255),
                               stroke_width=scale, stroke_fill=(5,12,32,240))
        canvas.alpha_composite(ink, (width*scale-ink.width, bottom*scale-ink.height))
    return canvas.resize((width, height), Image.Resampling.LANCZOS)


def restore(raw, built):
    require(len(raw) == len(built), 'Title member size changed')
    p, _ = texture_span(raw)
    result = bytearray(built)
    x0, y0, x1, y1 = BOX
    for y in range(y0, y1):
        at = p + (y*SIZE[0]+x0)*4
        result[at:at+(x1-x0)*4] = raw[at:at+(x1-x0)*4]
    return bytes(result)


def apply(raw, base, font, version):
    title.audit(raw)
    p, size = texture_span(raw)
    require(sha(raw[p:p+size]) == BACKGROUND_SHA, 'Title background source changed')
    require(len(base) == len(raw) and base[:GTF] == raw[:GTF], 'Title animation bytes changed')
    require(base[p:p+size] == raw[p:p+size], 'Title background already modified; refusing stale/composed footer')
    tile = background(raw).crop(BOX)
    tile.alpha_composite(overlay(font, version))
    r, g, b, a = tile.split()
    pixels = Image.merge('RGBA', (a,r,g,b)).tobytes()
    x0, y0, x1, y1 = BOX
    out = bytearray(base); stride = (x1-x0)*4
    for row in range(y1-y0):
        at = p + ((y0+row)*SIZE[0]+x0)*4
        out[at:at+stride] = pixels[row*stride:(row+1)*stride]
    result = bytes(out)
    require(result != base and restore(raw, result) == base, 'Changes outside footer rectangle')
    return result


def verify(raw, built, font, version):
    base = restore(raw, built)
    require(built == apply(raw, base, font, version), 'Missing or wrong-version Retro Trans footer')
    return dict(verified=True, version=version, credit=CREDIT, asset=EFF+':'+str(MEMBER),
                texture=TEXTURE, source_sha256=sha(raw), output_sha256=sha(built),
                background_sha256=BACKGROUND_SHA, box=list(BOX), font_size=FONT_SIZE,
                font_path=str(Path(font).resolve()), font_sha256=sha(Path(font).read_bytes()),
                title_animation_and_other_textures_preserved=True)


def check_packed(build, report):
    version = report['title_footer_version']
    require(report['version'] == version, 'Footer/build version mismatch')
    manifest = json.loads((Path(build)/'build_manifest.json').read_text(encoding='utf8'))
    require(manifest['version'] == version and manifest['title_footer_version'] == version
            and manifest['title_footer_credit'] == CREDIT and manifest['verified'], 'Invalid build version stamp')
    original, output = CPK(str(ROOT/'work/pkg'/EFF)), CPK(str(Path(build)/'RPCS3/NPJB00689'/EFF))
    get = lambda c: c.read(next(e for e in c.files if e['id'] == MEMBER))
    proof = verify(get(original), get(output), report['title_footer']['font_path'], version)
    require(proof == report['title_footer'], 'Packed title footer differs from recorded proof')
    require(manifest['files'] == report['game_files'], 'Version stamp inventory differs')
    return proof


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version'); ap.add_argument('--font', type=Path, default=DEFAULT_FONT)
    ap.add_argument('--out', type=Path, default=ROOT/'work/title024_footer_preview')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    version = build_version.next_version(requested_version=args.version)
    out = args.out.resolve()
    require(ROOT/'work' in out.parents and not out.exists(), 'Use a fresh work preview directory')
    c = CPK(str(ROOT/'work/pkg'/EFF)); raw = c.read(next(e for e in c.files if e['id'] == MEMBER))
    built = apply(raw, raw, args.font, version)
    proof = verify(raw, built, args.font, version)
    print(json.dumps(proof, indent=2)); print('New preview:', out)
    if not args.write:
        print('DRY RUN; --write creates previews only. No build number is consumed.'); return
    out.mkdir(parents=True)
    background(raw).save(out/'title_background_original.png')
    background(built).save(out/'title_background_footer.png')
    background(built).crop((880,616,1280,720)).save(out/'title_footer_corner.png')
    (out/'VALIDATION.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    main()
