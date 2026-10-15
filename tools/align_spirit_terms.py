"""Compare Z3 Spirit identities and preview Rengoku terminology fixes.

The sibling is a read-only reference. No effects, costs, durations, source
records or unrelated Fighting Spirit pilot skills are changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

import localization

ROOT = Path(__file__).resolve().parents[1]
SIBLING = ROOT.parent / 'SRW Z3'
AUDIT = ROOT / 'analysis/spirit_alignment.json'


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def reference(family):
    source = SIBLING / 'localization/messages' / (family + '.json')
    locale = SIBLING / 'localization/locales/en' / (family + '.json')
    names = {r['source']: read(locale)['messages'][k]['text']
             for k, r in read(source)['messages'].items()}
    hashes = {str(p.relative_to(SIBLING)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (source, locale)}
    return names, hashes


def target(jp, english, names):
    if jp in names:
        return names[jp]
    if jp == '闘':
        return names['闘志']
    if jp == '直':
        return names['直撃']
    # Native fixed-cell strips have their own renderer; retain Japanese order.
    if jp in ('熱魂闘閃不鉄集必加覚手狙突直幸努乱',
              '熱魂闘閃不鉄集必加覚手狙突直／乱分'):
        commands = ('熱血', '魂', '闘志', '閃き', '不屈', '鉄壁', '集中',
                    '必中', '加速', '覚醒', 'てかげん', '狙撃', '突撃', '直撃',
                    '幸運', '努力', 'かく乱', '分析')
        flags = dict(zip('熱魂闘閃不鉄集必加覚手狙突直幸努乱分', commands))
        return ' ／ '.join(', '.join(names[flags[ch]] for ch in part)
                          for part in jp.split('／'))
    # Multiline lists are keyed by Japanese identity rather than English word.
    if '\n' in jp and all(s in names or not s.strip() for s in jp.split('\n')):
        return '\n'.join(names.get(s, s) for s in jp.split('\n'))
    if '直撃' in jp and '闘志' not in jp:
        english = re.sub(r'\bFury\b', names['直撃'], english)
    if '闘志' in jp:
        english = re.sub(r'\bFighting Spirit\b', names['闘志'], english)
    return english


def plan():
    names, hashes = reference('spirits')
    effects, effect_hashes = reference('spirit_hook')
    hashes.update(effect_hashes)
    assert names['直撃'] == 'Break' and names['闘志'] == 'Fury'
    glossary = localization.terms()
    outputs, changes, comparison, descriptions = {}, [], [], []
    examined = 0
    for path in sorted((ROOT / 'localization/locales/en').glob('*.json')):
        doc = read(path)
        changed = False
        for key, row in doc.get('messages', {}).items():
            examined += 1
            jp, old = row.get('source'), row.get('text')
            if not jp or not old or row.get('status', '').startswith('excluded_'):
                continue
            new = target(jp, old, names)
            if new != old:
                from non_dialogue import validate_target
                validate_target(jp, new, glossary)
                changes.append(dict(catalog=path.relative_to(ROOT).as_posix(), id=key,
                                    source=jp, previous=old, text=new))
                row['text'] = new
                row['spirit_terminology_review'] = 'analysis/spirit_alignment.json'
                changed = True
            if jp in names:
                comparison.append(dict(id=key, source=jp, z3=names[jp], rengoku=new))
            if jp in effects:
                descriptions.append(dict(id=key, source=jp, z3=effects[jp], rengoku=new,
                    same_words=effects[jp].split() == new.split()))
        if changed:
            outputs[path] = doc
    present = {r['source'] for r in comparison}
    audit = dict(date='2026-10-15', sibling_reference_sha256=hashes,
                 examined_locale_records=examined, shared_command_names=len(present),
                 command_name_entries=len(comparison),
                 sibling_only_commands=sorted(set(names)-present),
                 matched_description_entries=len(descriptions),
                 command_names=comparison, descriptions=descriptions, changes=changes,
                 do_not_touch={'直撃': 'Break', '闘志': 'Fury', '戦意高揚': 'Fighting Sp'},
                 note='Identity/terminology alignment only. Preserve Rengoku effects, costs, '
                      'durations and unrelated pilot skills. No build or release created; '
                      'runtime screens untested. Native strip cells: 闘=Fu, 直=Br.')
    return outputs, audit


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    outputs, audit = plan()
    for change in audit['changes']:
        print(json.dumps(change, ensure_ascii=False))
    print(json.dumps({k: v for k, v in audit.items() if k not in
                      ('command_names', 'descriptions', 'changes', 'sibling_reference_sha256')},
                     ensure_ascii=False, indent=2))
    if args.write:
        for path, doc in outputs.items():
            path.write_text(localization.encoded(doc), encoding='utf8')
        # Preserve the first applied migration when rerun idempotently.
        if AUDIT.exists():
            previous = read(AUDIT)
            audit['changes'] = previous.get('changes', []) + audit['changes']
        AUDIT.write_text(localization.encoded(audit), encoding='utf8')
    else:
        print('DRY RUN; --write applies only the displayed terminology changes.')


if __name__ == '__main__':
    main()
