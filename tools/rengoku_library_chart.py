"""Library menu sprites and the separate Scenario Chart labels, NPJB00689.

All source/animation bindings are Rengoku's own. Compose with the English
title patch; never write originals. CLI defaults to a concrete dry-run.
"""
import argparse
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from cpk import CPK
import rengoku_title_art as title
from rengoku_chapter_art import paint
from rengoku_runtime import require, sha, DEFAULT_FONT, cell
from rengoku_screenshot_layout import line_width

ROOT = Path(__file__).resolve().parents[1]
EFF = title.EFF
MENU_SHA = '9dd1a7c0cad161d779314b76b96b3aef79174f439a474f2333b07b048b65685e'
CHARTS = {
    131: (0x62c00, '506211bffce00c9a456b7554929cbc721c0320f6683e07f824d5d8a844085414'),
    132: (0x1a0, '483094a98aaad3d9dd55647f427a948ea2320ee0def56613df75bc051a3877c1'),
}
# Native shared texture 5 in EFF 133; animation lives in EFF 134.
# rectangle, English, normal samples, transition samples.
MENU = (
    ((0, 272, 272, 56), 'Robot Encyclopedia', 1072, 20),
    ((0, 208, 312, 48), 'Character Encyclopedia', 1062, 20),
    ((0, 136, 168, 56), 'Glossary', 1052, 20),
    ((0, 72, 304, 48), 'Sound Select', 1042, 20),
    ((0, 8, 304, 56), 'Scenario Chart', 1032, 20),
)
HEADER = (96, 14, 472, 66)
FONT = Path('C:/Windows/Fonts/timesbd.ttf')


def config():
    return json.loads((ROOT / 'localization/library_chart.json').read_text(encoding='utf8'))


def background():
    row = config()['background']; path = ROOT / row['path']
    require(sha(path.read_bytes()) == row['sha256'], 'Unreviewed chart background')
    with Image.open(path) as im:
        return im.convert('RGBA').resize((1280, 720), Image.Resampling.LANCZOS)


def atlas(raw, gtf, texture):
    p = gtf + 12 + texture * 36
    require(raw[p + 12] == 0xa5, 'Expected linear ARGB32')
    w, h = struct.unpack_from('>HH', raw, p + 20)
    off, size = struct.unpack_from('>II', raw, p + 4)
    require(size == w * h * 4, 'Unexpected texture layout')
    return Image.frombytes('RGBA', (w, h), raw[gtf + off:gtf + off + size], 'raw', 'ARGB')


def menu_tile(rect, text):
    # Same supersampled Times Bold recipe used by Z3.1's Library buttons.
    _, _, w, h = rect
    face = ImageFont.truetype(str(FONT), 42 * 4)
    l, t, r, b = face.getbbox(text)
    ink = Image.new('RGBA', (r - l, b - t))
    ImageDraw.Draw(ink).text((-l, -t), text, font=face, fill='white')
    width, height = min(w - 16, round(ink.width / 4)), min(h - 16, round(ink.height / 4))
    ink = ink.resize((width, height), Image.Resampling.LANCZOS)
    tile = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    tile.alpha_composite(ink, ((w - width) // 2, (h - height) // 2))
    box = tile.getchannel('A').getbbox()
    require(box and box[0] >= 7 and box[2] <= w - 7 and box[1] >= 7 and box[3] <= h - 7,
            'Library label clips: ' + text)
    glow = Image.new('RGBA', (w, h), (182, 182, 182, 0))
    glow.putalpha(tile.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(
        ImageFilter.GaussianBlur(5)).point(lambda a: round(a * 176 / 255)))
    glow.alpha_composite(tile)
    return glow


def menu_apply(raw, animation, base):
    title.audit(raw)
    require(sha(animation) == MENU_SHA, 'Library animation source changed')
    title.verify(raw, base)
    require([r['text'] for r in config()['library']] == [en for _, en, *_ in MENU], 'Library display text changed')
    require(atlas(raw, title.GTF, 5).size == (664, 360), 'Rengoku menu atlas')
    out = bytearray(base)
    for rect, en, normal, transition in MENU:
        for mode, count in ((0x101, normal), (0x201, transition)):
            pattern = struct.pack('>8H', 0, *rect, 0x5000, mode, 5)
            require(animation.count(pattern) == count, 'Library sample count: ' + en)
        paint(out, title.GTF, 5, rect, menu_tile(rect, en))
    verify_regions(base, bytes(out), title.GTF, [(5, r) for r, *_ in MENU])
    return bytes(out)


def header_tile(font=DEFAULT_FONT):
    # This is a code-rendered UI label, like the existing chapter/font atlas
    # tooling. Its backing uses the new generated texture, never source art.
    x, y, w, h = HEADER
    tile = background().crop((x, y, x + w, y + h))
    face = ImageFont.truetype(str(font), 45 * 4)
    text = config()['heading']; l, t, r, b = face.getbbox(text)
    mask = Image.new('L', (r - l + 32, b - t + 32))
    ImageDraw.Draw(mask).text((16 - l, 16 - t), text, font=face, fill=255)
    mask = mask.resize((min(w - 32, round(mask.width / 4)), min(h - 20, round(mask.height / 4))), Image.Resampling.LANCZOS)
    full = Image.new('L', (w, h)); full.paste(mask, ((w - mask.width) // 2, (h - mask.height) // 2))
    glow = Image.new('RGBA', (w, h), (81, 255, 218, 0))
    glow.putalpha(full.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3)))
    edge = Image.new('RGBA', (w, h), (165, 255, 229, 0)); edge.putalpha(full.filter(ImageFilter.MaxFilter(3)))
    ink = Image.new('RGBA', (w, h), (0, 15, 14, 0)); ink.putalpha(full)
    for layer in (glow, edge, ink): tile.alpha_composite(layer)
    return tile


def chart_apply(raw, mid, font=DEFAULT_FONT):
    gtf, fingerprint = CHARTS[mid]
    require(sha(raw) == fingerprint, 'Rengoku chart source changed')
    require(atlas(raw, gtf, 1).size == (1280, 720), 'Chart atlas dimensions')
    out = bytearray(raw); regions = [(1, HEADER)]
    paint(out, gtf, 1, HEADER, header_tile(font))
    if mid == 131:
        require(raw[:gtf].count(struct.pack('>8H', 0, 0, 0, 1280, 720, 0x5000, 0x101, 2)) == 600,
                'Chart background animation samples')
        require(raw[:gtf].count(struct.pack('>8H', 0, 0, 0, 1280, 128, 0x5000, 0x101, 1)) == 600,
                'Chart heading animation samples')
        paint(out, gtf, 2, (0, 0, 1280, 720), background())
        regions.append((2, (0, 0, 1280, 720)))
    verify_regions(raw, bytes(out), gtf, regions)
    return bytes(out)


def verify_regions(base, built, gtf, regions):
    require(len(base) == len(built) and base != built, 'Missing/sized artwork mutation')
    restored = bytearray(built)
    for tex, (x, y, w, h) in regions:
        p = gtf + 12 + tex * 36
        tw = struct.unpack_from('>H', base, p + 20)[0]
        off = gtf + struct.unpack_from('>I', base, p + 4)[0]
        for yy in range(y, y + h):
            q = off + (yy * tw + x) * 4
            restored[q:q + w * 4] = base[q:q + w * 4]
    require(bytes(restored) == base, 'Unrelated artwork, geometry or animation changed')


def chapter_hooks(codec, rows, elf):
    # Rengoku's chart routine draws two independent UTF-8 strings at
    # 1b8a40 / 1b8a94; converted_stub applies the exact CP932 lookup.
    require(elf[0x1b8a20 - 0x10000:0x1b8a24 - 0x10000] == bytes.fromhex('480221b5'),
            'Chart episode formatter call changed')
    require(elf[0x1b8a54 - 0x10000:0x1b8a58 - 0x10000] == bytes.fromhex('48021ca1'),
            'Chart title getter changed')
    toc = 0x953f88
    for displacement, expected in ((-0x48b4, b'%s%s%s\0'), (-0x48b8, '『\0'.encode()), (-0x48bc, '』\0'.encode())):
        ptr = struct.unpack_from('>I', elf, toc + displacement - 0x10000)[0] - 0x10000
        require(elf[ptr:ptr + len(expected)] == expected, 'Chart wrapper format changed')
    titles = [r for r in rows if r['asset'] == 'work/eboot/EBOOT.ELF' and 0x873158 <= r['offset'] <= 0x8732b8]
    titles = [r for r in titles if r['jp'] not in ('クリアデータ', 'エーストークデータ', '終了メッセージデータ')]
    require(len(titles) == 15, 'Chart needs all 15 chapter titles')
    result = {}; report = []
    for n in range(1, 100):
        digits = ''.join(chr(0xff10 + int(c)) for c in str(n))
        text = 'Episode %d' % n
        # The chart caller passes 36px width / 40px height to 1bca18.
        require(line_width(codec, text, 36) < 214, 'Episode prefix overlaps title')
        result[('第' + digits + '話').encode('cp932')] = codec.encode(text)
    result['最終話'.encode('cp932')] = codec.encode('Final Episode')
    for r in titles:
        en = r['english']; require(line_width(codec, en, 36) < 800, 'Chart title exceeds panel')
        result[('『' + r['jp'] + '』').encode('cp932')] = codec.encode(en)
        report.append({'source': r['jp'], 'english': en, 'width_at_36px': line_width(codec, en, 36)})
    return result, report


def prepare(asset, title_base, font=DEFAULT_FONT):
    raw = asset('work/pkg/' + EFF + ':133')
    animation = asset('work/pkg/' + EFF + ':134')
    result = {(EFF, 133): menu_apply(raw, animation, title_base)}
    for mid in CHARTS:
        result[(EFF, mid)] = chart_apply(asset('work/pkg/' + EFF + ':' + str(mid)), mid, font)
    return result, {'menu_labels': [en for _, en, *_ in MENU],
                    'menu_animation_samples': sum(a + b for _, _, a, b in MENU),
                    'chart_heading': config()['heading'], 'background': config()['background'],
                    'members': {str(mid): sha(data) for (_, mid), data in result.items()},
                    'native_controls_nodes_animation_preserved': True}


def chart_proof(raw, codec=None, prefix='Episode 1', chapter='Green Earth'):
    """Local atlas composition and real glyph masks, not a gameplay capture."""
    page = atlas(raw, CHARTS[131][0], 2)
    ui = atlas(raw, CHARTS[131][0], 1)
    page.alpha_composite(ui.crop((0, 0, 1280, 128)))
    page.alpha_composite(ui.crop((192, 576, 1280, 704)), (96, 592))
    if codec is not None:
        def draw(text, x, y):
            for ch in text:
                code = codec.codes[ch]
                mask = codec.glyphs[code].resize((36, 40), Image.Resampling.LANCZOS)
                tile = Image.new('RGBA', (36, 40), (255, 255, 255, 0)); tile.putalpha(mask)
                page.alpha_composite(tile, (round(x), y))
                x += codec.widths[cell(code)] * 36 / 32
        draw(prefix, 140, 628); draw(chapter, 354, 628)
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true'); ap.add_argument('--out', type=Path, default=ROOT / 'work/menu011_preview')
    args = ap.parse_args(); out = args.out.resolve()
    require(ROOT / 'work' in out.parents and not out.exists(), 'Use fresh work preview folder')
    c = CPK(str(ROOT / 'work/pkg' / EFF))
    def asset(key): return c.read(next(e for e in c.files if e['id'] == int(key.rsplit(':', 1)[1])))
    result, report = prepare(asset, title.apply(asset('x:133')))
    print(json.dumps(report, indent=2, ensure_ascii=False)); print('Preview folder:', out)
    if not args.write: print('DRY RUN'); return
    out.mkdir(parents=True)
    atlas(result[(EFF, 133)], title.GTF, 5).save(out / 'library_buttons.png')
    chart_proof(result[(EFF, 131)]).save(out / 'flowchart_artwork.png')


if __name__ == '__main__': main()
