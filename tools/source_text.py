"""Read-only source parsers. No font mappings, target IDs or English injected."""
import re
import struct

LONG_OPEN = re.compile(r'\[(=*)\[')
JAPANESE = re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9d]')


def lua_strings(text):
    """Lex literal spans, skipping comments and respecting quoted strings.

    Offsets here are Unicode indices; callers explicitly map them to cp932
    byte offsets. Returned source contents keep escapes exactly as written.
    This locates literals, not dialogue roles or Lua runtime values.
    """
    index = 0
    while index < len(text):
        comment = text.startswith('--', index)
        start = index + 2 if comment else index
        opening = LONG_OPEN.match(text, start)
        if opening:
            closing = ']' + opening.group(1) + ']'
            end = text.find(closing, opening.end())
            if end < 0:
                raise ValueError('unterminated Lua long string/comment at %d' % index)
            if not comment:
                yield {'kind': 'long', 'start': index, 'end': end + len(closing),
                       'content_start': opening.end(), 'content_end': end,
                       'text': text[opening.end():end]}
            index = end + len(closing)
        elif comment:
            end = text.find('\n', index)
            index = len(text) if end < 0 else end + 1
        elif text[index] in ('\"', "'"):
            quote, start = text[index], index
            index += 1
            while index < len(text) and text[index] != quote:
                if text[index] == '\\':
                    index += 2
                    if index <= len(text) and text[index - 1] == '\r' and text[index:index + 1] == '\n':
                        index += 1
                else:
                    if text[index] in '\r\n':
                        raise ValueError('newline in Lua quoted string at %d' % start)
                    index += 1
            if index >= len(text):
                raise ValueError('unterminated Lua quoted string at %d' % start)
            yield {'kind': 'quoted', 'start': start, 'end': index + 1,
                   'content_start': start + 1, 'content_end': index,
                   'text': text[start + 1:index]}
            index += 1
        else:
            index += 1


def byte_offsets(text):
    result = [0]
    for character in text:
        result.append(result[-1] + len(character.encode('cp932')))
    return result


def rpw_chunks(data):
    if not data.startswith(b'<mt>prod#1') or data[20:24] != b'1.00':
        raise ValueError('unrecognized RPW header')
    total, body = struct.unpack_from('<II', data, 24)
    if total != len(data) or body != total - 60:
        raise ValueError('RPW file size mismatch')
    position, result = 32, []
    while data[position:position + 12] == b'<chunk-head>':
        name = data[position + 12:position + 20].rstrip(b'\0').decode('ascii')
        length, body_size = struct.unpack_from('<II', data, position + 20)
        start, end = position + 28, position + 28 + body_size
        chunk_end = position + length
        if not start <= end < chunk_end <= len(data) or data[end:end + 12] != b'<chunk-foot>':
            raise ValueError('invalid RPW chunk bounds: ' + name)
        footer_size = struct.unpack_from('<I', data, end + 12)[0]
        if end + footer_size != chunk_end or data[chunk_end - 12:chunk_end] != b'<endofchunk>':
            raise ValueError('invalid RPW chunk footer: ' + name)
        result.append({'name': name, 'offset': position, 'body_offset': start, 'body_end': end, 'end': chunk_end})
        position = chunk_end
    if data[position:position + 12] != b'<file--foot>' or position + 28 != len(data):
        raise ValueError('unparsed RPW trailer')
    return result


def rpw_strings(data):
    chunks = [c for c in rpw_chunks(data) if c['name'] == 'j-string']
    if len(chunks) != 1:
        raise ValueError('expected one RPW j-string chunk')
    chunk = chunks[0]
    position = chunk['body_offset']
    for ordinal, raw in enumerate(data[position:chunk['body_end']].split(b'\0')):
        yield {'ordinal': ordinal, 'offset': position, 'bytes': len(raw),
               'body_offset': position - chunk['body_offset'], 'jp': raw.decode('cp932'),
               'terminal_empty': position == chunk['body_end']}
        position += len(raw) + 1


def library_fields(raw):
    data = bytes(x if x in (0, 0x5e) else x ^ 0x5e for x in raw)
    if data[:8] not in (b'ZKANKYWD', b'ZKANCHAR', b'ZKANROBO'):
        raise ValueError('unknown library magic')
    if len(data) < 32 or data[16:20] != b'DSIZ' or data[24:28] != b'DATA':
        raise ValueError('invalid library wrapper')
    if struct.unpack_from('<I', data, 20)[0] != len(data) - 24 or struct.unpack_from('<I', data, 28)[0] != len(data) - 32:
        raise ValueError('library wrapper size mismatch')
    position, result = 32, []
    while position < len(data):
        if position + 8 > len(data):
            raise ValueError('truncated library field')
        tag = data[position:position + 4].decode('ascii')
        size = struct.unpack_from('<I', data, position + 4)[0]
        if not tag.isalnum() or position + 8 + size > len(data):
            raise ValueError('invalid library field bounds')
        payload = data[position + 8:position + 8 + size]
        try:
            text = payload.rstrip(b'\0').decode('cp932')
        except UnicodeDecodeError:
            text = None
        result.append({'tag': tag, 'offset': position + 8, 'bytes': size, 'text': text})
        position += 8 + size
    return data[:8].decode('ascii'), result


def nul_text_candidates(data):
    """Heuristic discovery only: whole NUL-delimited, printable cp932 runs.

    Does not identify binary record schemas, artwork, split labels or runtime
    consumers. No substitution uses this scanner's offsets automatically.
    """
    for match in re.finditer(rb'[^\x00]{2,}', data):
        raw = match.group()
        if len(raw) > 8192:
            continue
        try:
            text = raw.decode('cp932')
        except UnicodeDecodeError:
            continue
        if JAPANESE.search(text) and all(c.isprintable() or c in '\r\n\t' for c in text):
            yield {'offset': match.start(), 'bytes': len(raw), 'jp': text}
