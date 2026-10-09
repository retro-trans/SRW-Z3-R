"""Validate current source bindings and preview generated coverage/reading reports."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from non_dialogue import ROOT, SOURCE, LOCALE, digest, encoded, extract, validate_target, occurrence_text
import localization


def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def build():
    source=load('source/non_dialogue.json')
    locale=load('localization/locales/en/non_dialogue.json')
    art_source=load('source/artwork.json')
    art=load('localization/locales/en/artwork.json')
    glossary=localization.terms()
    assert locale['source_catalog_sha256']==digest(SOURCE.read_bytes())
    assert art['source_catalog_sha256']==digest((ROOT/'source/artwork.json').read_bytes())
    # Re-extract actual local assets, not only the cached Japanese catalog.
    fresh=extract()
    assert {r['id']:r for r in fresh['records']}=={r['id']:r for r in source['records']}, 'Source extraction no longer agrees'
    assert {r['asset']:r for r in fresh['assets']}=={r['asset']:r for r in source['assets']}, 'Source asset changed'
    assert Counter(encoded(r) for r in fresh['exclusions'])==Counter(encoded(r) for r in source['exclusions']), 'Exclusion inventory changed'
    rows={r['id']:r for r in source['records']}
    bound=[]
    for identity,v in locale['messages'].items():
        assert digest(v['source'].encode())==v['source_sha256'], identity
        for occurrence in v['occurrences']:
            assert rows[occurrence]['jp']==v['source'], identity
            bound.append(occurrence)
        if v['text']:
            validate_target(v['source'],v['text'],glossary)
            for occurrence in v.get('occurrence_overrides',{}):
                validate_target(v['source'],occurrence_text(v,occurrence),glossary)
        else:
            assert v['status'] in ('excluded_binary','excluded_charset','excluded_dialogue'), identity
    assert Counter(bound)==Counter(rows.keys()), 'Occurrence coverage mismatch'
    images={}
    for r in art_source['records']:
        v=art['messages'][r['id']]
        assert v['source']==r['source'] and v['source_sha256']==r['source_sha256']==digest(r['source'].encode())
        validate_target(r['source'],v['text'],glossary)
        if r['image'] not in images:
            images[r['image']]=digest((ROOT/r['image']).read_bytes())
        assert images[r['image']]==r['image_sha256'], r['image']
    refs=art_source['manual_screenshot_references']
    assert len(refs['ids'])==13
    for identity,sha in refs['source_guards'].items():
        assert locale['messages'][identity]['source_sha256']==sha

    reports=[]
    for path in sorted((ROOT/'work/non_dialogue_reviews').glob('*.json')):
        report=json.loads(path.read_text(encoding='utf-8'))
        reports.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path.read_bytes()),
                        'examined_count':report.get('examined_count',len(report.get('examined',[]))),
                        'english_reviewed_count':report.get('english_reviewed_count',len(report.get('english_reviewed',[]))),
                        'fixes':len(report.get('fixes',{})), 'uncertainties':len(report.get('uncertainties',[]))})
    stats=Counter(v['status'] for v in locale['messages'].values())
    groups=defaultdict(list)
    for identity,v in locale['messages'].items():
        groups[identity.split(':')[0]].append((identity,v))
    pending=[{'id':k,'source':v['source'],'text':v['text'],'notes':v.get('notes',''),'review':v.get('review'),
              'occurrences':v['occurrences']} for k,v in locale['messages'].items() if v['status']=='needs_review']

    # Classify the broad discovery pass without pretending byte scanning is OCR.
    discovery=load('work/text_coverage_candidates.json')
    known={(r['asset'],r.get('offset')) for r in source['records']}
    battle_source=load('source/battle_lines.json')
    battle_locale=load('localization/locales/en/battle_lines.json')
    battle_included={o for v in battle_locale['messages'].values() if v['status']!='excluded_binary' for o in v['occurrences']}
    battle_known={(r['asset'],r['offset']) for r in battle_source['records'] if r['id'] in battle_included}
    battle_excluded={(r['asset'],r['offset']) for r in battle_source['records'] if r['id'] not in battle_included}
    battle_remnants={(r['asset'],r['offset']) for r in battle_source['exclusions']}
    classified=Counter()
    uncertain=[]
    for r in discovery['unclassified_candidates']:
        asset,offset=r['asset'],r['offset']
        if (asset,offset) in known:
            kind='cataloged_source_occurrence'
        elif (asset,offset) in battle_known:
            kind='battle_source_occurrence'
        elif (asset,offset) in battle_excluded:
            kind='battle_binary_false_positive'
        elif (asset,offset) in battle_remnants:
            kind='battle_unreferenced_malformed_remnant'
        elif asset.endswith('KANJI-FIX.BN') or asset.endswith('EBOOT.ELF') and (0x80f000<=offset<0x831e00 or 0x948000<=offset<0x954070):
            kind='character_or_reading_table'
        elif '/SHADERS/' in asset:
            kind='developer_comments_cataloged_by_line'
        elif any(x in asset for x in ('EFFPS3.CPK:','MAPZ3RENPS3.CPK:','WP.CPK:','WCI.CPK:','BG.CPK:','RB.CPK:')):
            kind='binary_texture_candidates_visual_coverage_not_implied'
        else:
            kind='unclassified'
            uncertain.append({'asset':asset,'offset':offset,'sample':r['jp'][:80]})
        classified[kind]+=1
    limits=[
      'Draft catalogs only: no translated strings or images have been inserted into a playable game.',
      'NUL-delimited CP932/UTF-8 scanning is heuristic. Short strings, pointer consumers and embedded binary text are not exhaustively proven.',
      'Manual, startup screens, chapter cards, inspected menu atlases and common battle UI have visual transcriptions. Remaining robot/weapon/effect/map textures have not all been visually inspected.',
      'A small ambiguous mark in AID atlas 1_2 at roughly (126,128)-(176,177) may be geometry rather than text; its runtime use remains unresolved.',
      'DATA01.EDAT is a 496-byte opaque asset; no readable text was established from it.',
      'Character/reading tables, Japanese font glyphs and internal metadata are excluded. Story dialogue and battle speech have separate English catalogs; earlier immutable extraction exclusions record the previous scope.',
      'Original field lengths are extraction bounds, not English screen budgets. Font coverage, variable expansion widths, line wrapping and relocation remain untested.',
      'The encrypted executable was read with the supplied local RAP. The ELF is a verified text-extraction reconstruction, not a rebuilt executable.'
    ]
    coverage={'verified_on':'2026-09-25','source_catalog_sha256':digest(SOURCE.read_bytes()),
              'artwork_catalog_sha256':digest((ROOT/'source/artwork.json').read_bytes()),
              'source_occurrences':len(rows),'message_entries':len(locale['messages']),
              'english_entries':sum(bool(v['text']) and v['status']!='preserved_runtime' for v in locale['messages'].values()),
              'statuses':dict(stats),'artwork_blocks':len(art['messages']),'artwork_images_with_text':len(images),
              'effective_glossary_terms':len(glossary),'meaning_review_reports':len(reports),
              'source_exclusions':len(source['exclusions']),
              'broad_scan':{'report':'work/text_coverage_candidates.json','report_sha256':digest((ROOT/'work/text_coverage_candidates.json').read_bytes()),
                            'package_assets_examined':len(discovery['assets']),'elf_sections_examined':len(discovery['elf_sections']),
                            'candidate_count':len(discovery['unclassified_candidates']),'classifications':dict(classified),
                            'unclassified':uncertain},
              'limits':limits}
    outputs={'analysis/non_dialogue_coverage.json':encoded(coverage),
             'analysis/non_dialogue_review_index.json':encoded({'reports':reports,'notes':'Counts may overlap; retain guarded source/meaning reports under ignored work/. Applied terminology decisions are in analysis/non_dialogue_terminology_applied.json.'}),
             'analysis/non_dialogue_pending.json':encoded({'entries':pending,'note':'English drafts exist for every entry here. Flags concern readings, context or runtime composition.'})}
    lines=['# Non-dialogue English draft — 2026-09-25','',
           '%s English entries and %s artwork/manual blocks are drafted. %s catalog entries contain preserved engine keys; %s entries have explicit exclusions listed in the coverage report. No translatable catalog entry is left empty.' % (coverage['english_entries'],len(art['messages']),stats['preserved_runtime'],sum(v for k,v in stats.items() if k.startswith('excluded_'))),'',
           'This is translation source, not a playable patch. Story dialogue and battle speech are translated in separate catalogs; read [the battle draft](battle_lines_en.md) and [the project handoff](../HANDOFF.md). The sibling SRW Z3 glossary was the starting point; local research and explicit overrides are retained separately.','',
           '## Reading copies','', '| Category | English entries | Source occurrences | Longest English entry / line |','|---|---:|---:|---:|']
    for group,entries in groups.items():
        translated=[(k,v) for k,v in entries if v['text'] and v['status']!='preserved_runtime']
        longest=max((len(v['text']) for _,v in translated),default=0)
        line=max((len(line) for _,v in translated for line in v['text'].splitlines()),default=0)
        lines.append('| [%s](non_dialogue/%s.md) | %d | %d | %d / %d characters |' % (group.replace('_',' ').title(),group,len(translated),sum(len(v['occurrences']) for _,v in entries),longest,line))
        out=['# '+group.replace('_',' ').title()+' — English draft','','Generated from the canonical non-dialogue catalog. Source IDs identify review entries; lengths are not runtime limits.','']
        for identity,v in translated:
            out.extend(['## '+identity,'',v['text'],''])
            if v['status']=='needs_review':
                out.extend(['Review flag: '+v.get('notes','Context or reading remains provisional.'),''])
            if v.get('occurrence_overrides'):
                out.extend(['Occurrence-specific wording: '+', '.join(k+' = '+o['text'] for k,o in v['occurrence_overrides'].items()),''])
        outputs['docs/non_dialogue/'+group+'.md']='\n'.join(out)
    manual=['# English manual draft','','English transcription of the four supplied manual pages. Screenshots retain their original raster text; mapped screenshot labels are listed below. Historical support details and notices are translated as supplied.','']
    artwork=['# Artwork text draft','','Translations and region labels for inspected artwork. The original images are unchanged. Glyph atlases are character resources, not prose.','']
    previous={}
    for row in art_source['records']:
        dest=manual if '/manual/' in row['image'] and '/00' in row['image'] else artwork
        if previous.get(id(dest))!=row['image']:
            dest.extend(['## '+row['image'],''])
            previous[id(dest)]=row['image']
        dest.extend(['### '+row['region'],'',art['messages'][row['id']]['text'],''])
    manual.extend(['## Screenshot label references',''])
    manual.extend('- '+identity+': '+locale['messages'][identity]['text'] for identity in refs['ids'])
    outputs['docs/manual_en.md']='\n'.join(manual)+'\n'
    outputs['docs/artwork_en.md']='\n'.join(artwork)+'\n'
    lines.extend(['','Also read [the manual](manual_en.md) and [artwork labels](artwork_en.md).','',
                  '## Review and coverage','',
                  '%d occurrence bindings were re-extracted and checked against local source assets. %d guarded proof reports are indexed in `analysis/non_dialogue_review_index.json`. Meaning corrections preceded scripted terminology normalization. %d entries retain review flags; see `analysis/non_dialogue_pending.json`.' % (len(rows),len(reports),len(pending)),'',
                  'The broad discovery pass examined %d package assets and %d non-code ELF sections. Its %d candidates are classified in `analysis/non_dialogue_coverage.json`; this is a byte-scan inventory, not a claim that every raster image was inspected.' % (len(discovery['assets']),len(discovery['elf_sections']),len(discovery['unclassified_candidates'])),'',
                  'The inherited glossary has 1,168 entries; the effective glossary now has %d entries. Rengoku names, title spellings and explicit alternatives are recorded in `analysis/rengoku_terms.json` and `localization/glossary_additions.json`.' % len(glossary),'',
                  '## Remaining work',''])
    lines.extend('- '+line for line in limits)
    lines.extend(['','The 64-byte credit fields, 28-byte terrain names and indexed binary text spans are source-storage bounds only. Full English was retained. There is no verified maximum English character count or runtime screenshot measurement yet.','',
                  '## Checks','',
                  'Run `python -X utf8 tools/non_dialogue.py check`, `python -X utf8 tools/localization.py check`, `python -X utf8 tools/verify_source.py`, and `python -X utf8 -m unittest discover -s tests -v`. This report additionally re-extracts every catalog source binding and verifies artwork image hashes and screenshot cross-references.',''])
    outputs['docs/non_dialogue_status.md']='\n'.join(lines)
    return outputs,coverage


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    outputs,coverage=build()
    print('Validated source occurrences:',coverage['source_occurrences'],'English entries:',coverage['english_entries'],'artwork blocks:',coverage['artwork_blocks'])
    print('Broad scan classifications:',coverage['broad_scan']['classifications'])
    print('Statuses:',coverage['statuses'])
    print('Glossary:',coverage['effective_glossary_terms'],'review reports:',coverage['meaning_review_reports'])
    for path,body in outputs.items():
        print(path,len(body.encode()),'bytes',repr(body[:115]))
    if args.write:
        for relative,body in outputs.items():
            path=ROOT/relative
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(body,encoding='utf-8')
    else:
        print('DRY RUN; --write saves generated reports and reading copies.')


if __name__=='__main__':
    main()
