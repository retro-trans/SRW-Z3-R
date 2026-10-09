"""Extract and translate source-bound non-dialogue catalogs; writes require --write."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import struct
from cpk import CPK
import localization
import luarec
from source_text import lua_strings, byte_offsets, rpw_strings, library_fields, JAPANESE

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / 'work/pkg/USRDIR'
SOURCE = ROOT / 'source/non_dialogue.json'
LOCALE = ROOT / 'localization/locales/en/non_dialogue.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


# A space flag would misread prose such as "50% per turn" as a % p token.
# The extracted game's actual format strings use the flags below.
PRINTF = re.compile(r'%(?:\d+\$)?[-+#0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcsp%]')
RUNTIME = re.compile(r'【(?:必要容量|チェック容量|セーブデータ|セーブデータ詳|PS3改行|VITA改行|ストレージ|動作)】')
CONTROLS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]|\$[A-Za-z]|[《》]')


def validate_target(source, text, glossary):
    expanded = localization.expand(text, glossary)
    for label, pattern in [('printf tokens', PRINTF), ('runtime keys', RUNTIME), ('control markers', CONTROLS)]:
        if pattern.findall(source) != pattern.findall(expanded):
            raise ValueError(label + ' changed')
    prose = RUNTIME.sub('', expanded).replace('・', '')
    if JAPANESE.search(prose) or re.search(r'[\ue000-\uf8ff]', prose):
        raise ValueError('Unexpanded Japanese or private-use glyph')
    return expanded


def occurrence_text(entry, identity):
    if identity not in entry['occurrences']:
        raise ValueError('Unknown occurrence: ' + identity)
    return entry.get('occurrence_overrides', {}).get(identity, {}).get('text', entry['text'])


def mtfl_fields(raw):
    if raw[:8] != b'MTFLz2_2':
        raise ValueError('Unexpected MTFL header')
    n = struct.unpack_from('<I', raw, 0x40)[0]
    if not 1 <= n <= 1000:
        raise ValueError('Invalid MTFL record count')
    pos, records = 0x44, []
    for _ in range(n):
        fields = struct.unpack_from('<8I', raw, pos)
        marker, identity = struct.unpack_from('<II', raw, pos+32)
        if marker != 0xffffffff:
            raise ValueError('MTFL record separator mismatch')
        records.append((identity, fields))
        pos += 40
    base = pos + 16
    if raw[base+12:base+15] != bytes((0x81 ^ 0x7a, 0x91 ^ 0x7a, 0)) or sorted(i for i, _ in records) != list(range(n)):
        raise ValueError('Invalid MTFL text base/IDs')
    for identity, fields in records:
        for i, tag in enumerate(('WORD', 'SRCE', 'DSCR', 'DSC2')):
            off, size = fields[i*2:i*2+2]
            if base+off+size > len(raw):
                raise ValueError('MTFL text extent mismatch')
            data = raw[base+off:base+off+size]
            jp = bytes(c if c == 0x7a else c ^ 0x7a for c in data).decode('cp932')
            yield identity, tag, base+off, jp


def scan_nul(data):
    for m in re.finditer(rb'[^\x00]{2,}', data):
        for encoding in ('utf-8', 'cp932'):
            try:
                text = m[0].decode(encoding)
            except UnicodeDecodeError:
                continue
            if JAPANESE.search(text) and all(c.isprintable() or c in '\r\n\t\u3000' for c in text):
                yield m.start(), encoding, text
                break


def credit_fields(raw):
    """Credit records: 20-byte header, then 64 text + 30 metadata bytes."""
    count = struct.unpack_from('>H', raw, 0)[0]
    if len(raw) != 20 + count*94:
        raise ValueError('Invalid credits record extent')
    for i in range(count):
        offset = 20+i*94
        field = raw[offset:offset+64]
        end = field.index(b'\0')
        if any(field[end:]):
            raise ValueError('Nonzero credit text padding')
        text = field[:end].decode('cp932')
        if text.strip():
            yield offset, text


def recap_fields(raw):
    """Linked recap records have a 16-byte header and bounded CP932 text."""
    offset, seen = 0, set()
    while offset not in seen:
        seen.add(offset)
        identity = raw[offset:offset+4].decode('ascii')
        following = struct.unpack_from('>I', raw, offset+8)[0]
        end = following or len(raw)
        if (not re.fullmatch(r'10\d\d', identity) or raw[offset+4:offset+8] != b'\0'*4
                or raw[offset+12:offset+16] != b'\xff'*4 or not offset+16 < end <= len(raw)):
            raise ValueError('Invalid recap record')
        field = raw[offset+16:end]
        text, _, padding = field.partition(b'\0')
        if any(padding):
            raise ValueError('Invalid recap padding')
        yield identity, offset+16, text.decode('cp932')
        if not following:
            return
        offset = following
    raise ValueError('Cyclic recap records')


def map_fields(raw):
    count = struct.unpack_from('<I',raw,8)[0]
    base,size = struct.unpack_from('<II',raw,20)
    if base != 32 or size != 32*count or base+size > len(raw):
        raise ValueError('Invalid map terrain name table')
    for i in range(count):
        offset = base+32*i+4
        field = raw[offset:base+32*(i+1)]
        text,sep,padding = field.partition(b'\0')
        if not sep or any(padding):
            raise ValueError('Invalid map terrain name padding')
        if text:
            yield offset,text.decode('cp932')


def extract():
    rows, exclusions, assets = [], [], []
    def asset(path, member, data):
        key = str(path.relative_to(ROOT)).replace('\\', '/') + (':' + str(member) if member is not None else '')
        assets.append({'asset': key, 'sha256': digest(data), 'bytes': len(data)})
        return {'asset': key, 'asset_sha256': digest(data)}
    def add(meta, group, locator, jp, force=False, **extra):
        if not force and not JAPANESE.search(jp):
            return
        rows.append(dict(meta, group=group, locator=locator, jp=jp, **extra))
    for family in ('KW', 'PT', 'RT'):
        p = PKG / ('COMMONDATA_REN/MTDATA/MTZKN_' + family + '.CPK')
        cpk = CPK(str(p))
        for entry in cpk.files:
            raw = cpk.read(entry)
            meta = asset(p, entry['id'], raw)
            _, fields = library_fields(raw)
            for f in fields:
                if f['tag'] in ('WORD', 'SRCE', 'DSCR', 'DSC2', 'CHFN', 'CHNN', 'PRDC', 'ACTR', 'RBTN', 'RBN2', 'PLTN', 'HEIT', 'WEIT'):
                    if f['text'] is None:
                        raise ValueError('Undecodable library text')
                    add(meta, 'library', f['tag'], f['text'], offset=f['offset'], family=family, entry=entry['id'])
    p = PKG / 'COMMONDATA_REN/MTDATA/MTV_ALL_KEYWORD_DEF.CPK'
    cpk = CPK(str(p))
    for entry in cpk.files:
        raw = cpk.read(entry)
        meta = asset(p, entry['id'], raw)
        for identity, tag, offset, jp in mtfl_fields(raw):
            add(meta, 'library', '%d:%s' % (identity, tag), jp, offset=offset, family='MTFL', entry=identity)
    p = PKG / 'COMMONDATA_REN/MTDATA/RPW_DATA.CPK'
    cpk = CPK(str(p))
    for entry in cpk.files:
        raw = cpk.read(entry)
        meta = asset(p, entry['id'], raw)
        for r in rpw_strings(raw):
            # Reviewed every quoted source. The three spirit descriptions at
            # 24, 25, 30 are explicitly retained, even though they start in quotes.
            if r['ordinal'] in set(range(10, 24)) | {26, 27, 28, 29}:
                exclusions.append(dict(meta, locator=r['ordinal'], reason='spoken battle retreat line'))
            else:
                add(meta, 'gameplay', str(r['ordinal']), r['jp'], offset=r['offset'])
    def lua(meta, raw):
        text = raw.decode('cp932')
        offsets = byte_offsets(text)
        for r in lua_strings(text):
            if not JAPANESE.search(r['text']):
                continue
            context = text[max(0, r['start']-160):r['start']]
            if r['kind'] == 'long' and luarec.HEAD.search(context):
                exclusions.append(dict(meta, locator=offsets[r['start']], reason='speaker-tagged dialogue'))
                continue
            jp = r['text']
            if r['kind'] == 'quoted':
                jp = jp.replace('\\n', '\n').replace('\\r', '\r')
            add(meta, 'scenario', str(offsets[r['start']]), jp, offset=offsets[r['content_start']], literal_kind=r['kind'], raw_literal=r['text'], context=context[-160:])
    for p in sorted((ROOT / 'work/story').glob('*.lua')):
        raw = p.read_bytes()
        lua(asset(p, None, raw), raw)
    p = PKG / 'COMMONDATA_REN/KURODATA/LUACPKZ3REN.CPK'
    cpk = CPK(str(p))
    for entry in cpk.files:
        raw = cpk.read(entry)
        lua(asset(p, entry['id'], raw), raw)
    # Candidate strings carry discovery-only bindings. They are never patch offsets.
    p = ROOT / 'work/eboot/EBOOT.ELF'
    raw = p.read_bytes()
    meta = asset(p, None, raw)
    if digest(raw) != json.loads((ROOT / 'analysis/eboot_extraction.json').read_text())['elf_sha256']:
        raise ValueError('ELF fingerprint mismatch')
    for offset, encoding, jp in scan_nul(raw[0x831eb6:0x88f000]):
        add(meta, 'interface', hex(offset+0x831eb6), jp, offset=offset+0x831eb6, encoding=encoding, binding='text candidate; runtime consumer unverified')
    for offset, size in ((0x830f80, 32), (0x8317e0, 64)):
        for relative, encoding, jp in scan_nul(raw[offset:offset+size]):
            add(meta, 'interface', hex(offset+relative), jp, offset=offset+relative, encoding=encoding, binding='text candidate; runtime consumer unverified')
    # A second data section contains duplicate gameplay tables, DLC blurbs,
    # result screens and short UI labels. Exclude the adjacent battle dialogue.
    for start, end in ((0x954070, 0x959700), (0x95a550, 0x95a700),
                       (0x95d588, 0x95daa0), (0x95ffd6, 0x960000), (0x960260, 0x960290)):
        for relative, encoding, jp in scan_nul(raw[start:end]):
            offset = start+relative
            add(meta, 'interface', hex(offset), jp, offset=offset, encoding=encoding,
                binding='secondary ELF data section candidate; consumer unverified')
    for relative, encoding, jp in scan_nul(raw[0x959c18:0x959f80]):
        exclusions.append(dict(meta, locator=hex(0x959c18+relative), reason='spoken battle retreat line in ELF'))
    for start,end in ((0x95a528,0x95a558),(0x960286,0x960294)):
        for relative,encoding,jp in scan_nul(raw[start:end]):
            offset=start+relative
            add(meta,'interface',hex(offset)+':complete',jp,offset=offset,encoding=encoding,
                binding='complete source span at secondary scan boundary')
    start=0x95d5f8
    end=raw.index(b'\0',start)
    add(meta,'interface',hex(start),raw[start:end].decode('cp932'),offset=start,encoding='cp932',
        binding='confirmation string following packed single-byte symbol table')
    start=0x95a538
    end=raw.index(b'\0',start)
    add(meta,'interface',hex(start),raw[start:end].decode('cp932'),offset=start,encoding='cp932',
        binding='chapter title following binary metadata')
    p = PKG / 'DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'
    cpk = CPK(str(p))
    for entry in cpk.files:
        if entry['id'] not in (0, 4, 5, 6, 13, 14, 15):
            continue
        raw = cpk.read(entry)
        meta = asset(p, entry['id'], raw)
        mid = entry['id']
        if mid == 0:
            start, end = struct.unpack_from('>II', raw, 0x20)
            if raw[:4] != b'FSSA' or not 0 < start < end <= len(raw):
                raise ValueError('Invalid FSSA string pool')
            for relative, encoding, jp in scan_nul(raw[start:end]):
                offset = start+relative
                add(meta, 'menu_resource', hex(offset), jp, offset=offset, encoding=encoding, binding='FSSA string pool; consumers unverified')
        elif mid in (5, 6):
            if raw[:4] != (b'SB2T' if mid == 5 else b'UB2T') or raw[16:20] != b'DIXT':
                raise ValueError('Invalid indexed UI text')
            table_size = struct.unpack_from('>I', raw, 24)[0]
            tdxt = 32+table_size
            if raw[tdxt:tdxt+4] != b'TDXT':
                raise ValueError('Invalid indexed UI payload')
            base = tdxt+16
            encoding = 'cp932' if mid == 5 else 'utf-8'
            for i in range(table_size//4):
                offset = base+struct.unpack_from('>I', raw, 32+4*i)[0]
                end = raw.find(b'\0', offset)
                if not base <= offset <= end < len(raw):
                    raise ValueError('Invalid UI string offset')
                jp = raw[offset:end].decode(encoding)
                add(meta, 'menu_resource', 'index:%d' % i, jp, offset=offset, encoding=encoding, binding='DIXT index')
        elif mid == 4:
            exclusions.append(dict(meta, reason='Layout object identifiers; binary metadata, not display strings.'))
        else:
            if mid == 15:
                # The opening title starts after the 20-byte binary header.
                # Retain the earlier candidate for audit; classify it separately.
                end = raw.index(b'\0', 20)
                add(meta, 'credits', hex(20), raw[20:end].decode('cp932'), offset=20,
                    encoding='cp932', binding='opening title after binary header; consumer unverified')
            for offset, encoding, jp in scan_nul(raw):
                if re.search(r'[ぁ-ヿ一-龯]', jp) and not re.search(r'[ｦ-ﾟ]', jp):
                    add(meta, 'narration' if mid in (13, 14) else 'credits', hex(offset), jp, offset=offset, encoding=encoding, binding='text candidate; consumer unverified')
            if mid == 15:
                seen_offsets = {r['offset'] for r in rows if r['asset'] == meta['asset']}
                for offset, jp in credit_fields(raw):
                    if offset not in seen_offsets:
                        add(meta, 'credits', hex(offset), jp, force=True, offset=offset,
                            encoding='cp932', binding='64-byte credit field in 94-byte record')
    p = PKG / 'DATA_REN/KURODATA/KDATAPS3Z3REN.CPK'
    cpk = CPK(str(p))
    entry = next(e for e in cpk.files if e['id'] == 4)
    raw = cpk.read(entry)
    meta = asset(p, 4, raw)
    for identity, offset, jp in recap_fields(raw):
        add(meta, 'scenario', 'recap:'+identity, jp, offset=offset, encoding='cp932', binding='linked recap record; scenario summary, not spoken dialogue')
    p = ROOT / 'work/pkg/PARAM.SFO'
    raw = p.read_bytes()
    meta = asset(p, None, raw)
    for offset, encoding, jp in scan_nul(raw):
        add(meta, 'interface', hex(offset), jp, offset=offset, encoding=encoding, binding='package title metadata')
    p = PKG / 'DATA_REN/MAPETC/MAPZ3RENPS3.CPK'
    cpk = CPK(str(p))
    for entry in cpk.files:
        if entry['id']%4:
            continue
        raw = cpk.read(entry)
        meta = asset(p,entry['id'],raw)
        for offset,jp in map_fields(raw):
            add(meta,'map_terrain',hex(offset),jp,offset=offset,encoding='cp932',binding='28-byte name field in 32-byte terrain table record')
    for p in sorted((PKG/'SHADERS').iterdir()):
        if p.suffix.upper() not in ('.FCG','.VCG'):
            continue
        raw=p.read_bytes()
        lines=raw.decode('cp932').splitlines()
        if not any(JAPANESE.search(line) for line in lines):
            continue
        meta=asset(p,None,raw)
        for number,line in enumerate(lines,1):
            if JAPANESE.search(line):
                add(meta,'developer_comment','line:'+str(number),line.strip(),encoding='cp932',
                    binding='Japanese comment in shipped shader source; not player-facing text')
    for r in rows:
        r['id'] = 'nd:' + digest((r['asset'] + ':' + r['locator']).encode())[:20]
        r['source_sha256'] = digest(r['jp'].encode())
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate occurrence IDs')
    return {'schema': 1, 'assets': assets, 'records': rows, 'exclusions': exclusions,
            'limits': ['Executable candidate region verified by text inspection, not a complete pointer map.', 'Other non-executable sections contain charset and binary tables requiring classification.', 'Raster artwork and font atlases require visual inventory.', 'Candidates are not safe binary replacement positions.']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=('extract', 'seed', 'check'))
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if args.command == 'extract':
        source = extract()
        print('Occurrences:', len(source['records']), dict(Counter(r['group'] for r in source['records'])))
        print('Dialogue exclusions:', len(source['exclusions']))
        for group in ('library', 'gameplay', 'scenario', 'interface', 'menu_resource'):
            sample = [r for r in source['records'] if r['group'] == group][:3]
            for r in sample:
                print(group, r['locator'], repr(r['jp'][:120]))
        if args.write:
            if SOURCE.exists() and SOURCE.read_text(encoding='utf-8') != encoded(source):
                raise ValueError('Refusing differing source catalog')
            SOURCE.parent.mkdir(parents=True, exist_ok=True)
            SOURCE.write_text(encoded(source), encoding='utf-8')
    elif args.command == 'seed':
        source = json.loads(SOURCE.read_text(encoding='utf-8'))
        messages = {}
        groups = defaultdict(list)
        for r in source['records']:
            groups[(r['group'], r['jp'])].append(r)
        terms = defaultdict(set)
        for term in localization.terms():
            if term.get('en'):
                terms[term['jp']].add(term['en'])
        for (group, jp), rows in groups.items():
            key = group + ':' + digest(jp.encode())[:16]
            variants = terms.get(jp, set())
            text = next(iter(variants)) if len(variants) == 1 else None
            messages[key] = {'source': jp, 'text': text, 'status': 'glossary_draft' if text else 'untranslated', 'occurrences': [r['id'] for r in rows], 'source_sha256': digest(jp.encode())}
        output = {'schema': 1, 'language': 'en', 'source_catalog_sha256': digest(SOURCE.read_bytes()), 'messages': messages}
        print('Unique entries:', len(messages), dict(Counter(v['status'] for v in messages.values())))
        for k, v in [(k, v) for k, v in messages.items() if v['text']][:12]:
            print(k, v['source'], '->', v['text'])
        if args.write:
            if LOCALE.exists():
                raise ValueError('Existing locale; edit translations without reseeding')
            LOCALE.write_text(encoded(output), encoding='utf-8')
    else:
        source = json.loads(SOURCE.read_text(encoding='utf-8'))
        locale = json.loads(LOCALE.read_text(encoding='utf-8'))
        if locale['source_catalog_sha256'] != digest(SOURCE.read_bytes()):
            raise ValueError('Source catalog changed')
        rows = {r['id']: r for r in source['records']}
        seen = []
        glossary = localization.terms()
        for k, v in locale['messages'].items():
            if digest(v['source'].encode()) != v['source_sha256']:
                raise ValueError('Stale source: ' + k)
            for identity in v['occurrences']:
                if rows[identity]['jp'] != v['source']:
                    raise ValueError('Wrong source binding: ' + k)
                seen.append(identity)
            if v['text']:
                try:
                    validate_target(v['source'],v['text'],glossary)
                    for identity,override in v.get('occurrence_overrides',{}).items():
                        if not override.get('reason'):
                            raise ValueError('Undocumented occurrence override')
                        validate_target(v['source'],occurrence_text(v,identity),glossary)
                except ValueError as error:
                    raise ValueError(k + ': ' + str(error))
            elif v['status'] not in ('untranslated', 'excluded_binary', 'excluded_dialogue', 'excluded_charset'):
                raise ValueError('Missing target text: ' + k)
        if Counter(seen) != Counter(rows.keys()):
            raise ValueError('Missing or repeated source occurrences')
        print(dict(Counter(v['status'] for v in locale['messages'].values())))
        print('All source fingerprints and occurrence bindings agree.')
    if args.command != 'check' and not args.write:
        print('DRY RUN; pass --write after inspecting output.')


if __name__ == '__main__':
    main()
