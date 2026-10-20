"""Preview the source-reviewed Crowe referent fix; --write applies it."""
import argparse
import json
from pathlib import Path

import localization

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = 'rengoku:STGZ3REN_00021:00060'
OLD = ('$$ランド$$\n「Cut her some slack, $$セツコ$$.\n'
       '　Everyone\'s got someone they can\'t stand up to」')
NEW = OLD.replace('Cut her some slack', 'Cut him some slack')
JP = ('ランド\n「勘弁してやれよ、セツコ。\n'
      '　人間、誰しも頭の上がらない相手ってのがいるもんだ」')


def main(write):
    path = ROOT / 'localization/locales/en/STGZ3REN_00021.json'
    source = localization.read(ROOT / 'source/story/STGZ3REN_00021.json')
    row = next(r for r in source['records'] if r['id'] == IDENTITY)
    assert row['jp'].replace('\r\n', '\n') == JP, 'Source guard changed'
    doc = localization.read(path)
    entry = doc['messages'][IDENTITY]
    assert entry['text'] in (OLD, NEW), 'English changed since meaning review'
    errors, _ = localization.validate(row, entry, localization.terms())
    assert not errors, errors
    changed = entry['text'] != NEW
    print(IDENTITY, repr(entry['text']), '->', repr(NEW))
    print('Rand addresses Setsuko about Crowe, following records58–59; '
          'no reference/name/wrapper/source-binding change.')
    entry['text'] = NEW
    note = ('2026-10-20 CDS/context review: Rand asks Setsuko to ease up on '
            'Crowe, whose reply is in row59. Corrected her to him.')
    if note not in entry.setdefault('notes', []):
        entry['notes'].append(note)
    errors, _ = localization.validate(row, entry, localization.terms())
    assert not errors, errors
    report = dict(date='2026-10-20', story_slice=dict(member='STGZ3REN_00021',
        in_slice_indexes=[0,79], in_slice_examined=80, adjacent_indexes=[80,89],
        adjacent_examined=10, distinct_story_records_examined=90),
        screenshot_dialogue='rengoku:STGZ3REN_00021:00079',
        screenshot_dialogue_retained=True,
        library_identities=['193ac9bcadfa95cc','38d47eb0c382cfe2','568f903d92f3201f'],
        library_interface_entries_reviewed=6, bound_source_occurrences_reviewed=14,
        screenshot_findings=['Dialogue conveys rising debt accurately.',
            'Real coin-drop sound and 1 G per activation are explicit in Japanese.',
            'Accumulated million-G debt is not the cost of one activation.',
            'Contextual keyword label and library heading may differ in English.'],
        corrections=[dict(id=IDENTITY,previous=OLD,text=NEW,
            reason='Crowe is the object of Rand\'s appeal to Setsuko.')],
        unresolved_requested_meanings=[],build_created=False,release_created=False,
        note='Source review only; screenshot passages retained. Incidental pronoun '
             'fix is not in public v0.1.5; no version consumed.')
    print('Canonical changes:', int(changed), '; requested screenshot changes: 0')
    if not write:
        print('DRY RUN: --write applies the one reviewed pronoun fix and saves audit.')
        return
    if changed:
        path.write_text(localization.encoded(doc), encoding='utf8')
    (ROOT / 'analysis/cds_translation_review.json').write_text(
        localization.encoded(report), encoding='utf8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    main(ap.parse_args().write)
