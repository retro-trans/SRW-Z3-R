"""Preview all source-guarded battle drafts and independent meaning corrections."""
import argparse
from collections import Counter
import json
from pathlib import Path
from battle_lines import ROOT, SOURCE, LOCALE, check_target, BINARY_CANDIDATES
from non_dialogue import digest, encoded
import localization

EXCLUDED=BINARY_CANDIDATES


def assemble(require_reviews=True):
    locale=json.loads(LOCALE.read_bytes())
    if locale['source_catalog_sha256']!=digest(SOURCE.read_bytes()):
        raise ValueError('Battle source changed')
    original={k:dict(v) for k,v in locale['messages'].items()}
    items=list(original.items());glossary=localization.terms()
    indexes=[];review_indexes=[];reviewed=set();seen=set();fixes=[]
    for start in range(0,len(items),80):
        path=ROOT/'work/battle_batches'/('%04d.json'%start)
        proposal=json.loads(path.read_bytes())
        if proposal['source_catalog_sha256']!=locale['source_catalog_sha256']:
            raise ValueError('Stale draft: '+str(path))
        expected={k for k,v in items[start:start+80] if k not in EXCLUDED}
        if set(proposal['translations'])!=expected:
            raise ValueError('Wrong draft slice coverage: '+str(path))
        for k,v in proposal['translations'].items():
            entry=locale['messages'][k]
            if k in seen or entry['source_sha256']!=v['source_sha256']:
                raise ValueError('Stale/duplicate source: '+k)
            seen.add(k)
            check_target(entry['source'],v['text'],glossary)
            entry.update(text=v['text'],status=v.get('status','draft'),notes=v.get('notes',''),batch=path.relative_to(ROOT).as_posix())
        indexes.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path.read_bytes()),'start':start,
                        'translated':len(expected),'report':proposal.get('report',{})})
        review_path=ROOT/'work/battle_reviews'/('%04d.json'%start)
        if not review_path.exists():
            if require_reviews:raise ValueError('Missing independent review: '+str(review_path))
            continue
        review=json.loads(review_path.read_bytes())
        if review['source_catalog_sha256']!=locale['source_catalog_sha256'] or review['proposal_sha256']!=digest(path.read_bytes()):
            raise ValueError('Stale review: '+str(review_path))
        examined=set(review['examined'])
        if not expected<=examined:raise ValueError('Unreviewed slice records: '+str(review_path))
        reviewed.update(expected)
        for k,fix in review.get('fixes',{}).items():
            if k not in expected:raise ValueError('Out-of-slice fix: '+k)
            entry=locale['messages'][k]
            if fix['source_sha256']!=entry['source_sha256'] or fix['previous']!=entry['text']:
                raise ValueError('Stale meaning correction: '+k)
            check_target(entry['source'],fix['text'],glossary)
            entry.update(text=fix['text'],status=fix.get('status',entry['status']))
            entry['notes']=(entry.get('notes','')+' Meaning proof: '+fix['reason']).strip()
            fixes.append(dict(id=k,**fix))
            print('MEANING',k,repr(fix['previous']),'=>',repr(fix['text']),fix['reason'])
        for flag in review.get('uncertainties',[]):
            k=flag['id']
            if k not in expected:raise ValueError('Out-of-slice uncertainty: '+k)
            entry=locale['messages'][k];entry['status']='needs_review'
            entry['notes']=(entry.get('notes','')+' Independent proof: '+flag['note']).strip()
        for k in expected:locale['messages'][k]['meaning_review']=review_path.relative_to(ROOT).as_posix()
        review_indexes.append({'path':review_path.relative_to(ROOT).as_posix(),'sha256':digest(review_path.read_bytes()),
                               'reviewer':review['reviewer'],'rows_in_slice':len(expected),'rows_examined':review['rows_examined'],
                               'fixes':len(review.get('fixes',{})),'uncertainties':len(review.get('uncertainties',[]))})
    for k,jp in EXCLUDED.items():
        entry=locale['messages'][k]
        if entry['source']!=jp or entry['source_sha256']!=digest(jp.encode()):raise ValueError('Exclusion source changed')
        entry.update(text=None,status='excluded_binary',notes='Two short false CP932 matches after the final ELF retreat quote, outside the quoted text pool. Immutable discovery source retained.')
    if len(seen)!=3575:raise ValueError('Incomplete battle draft coverage')
    for k,v in locale['messages'].items():
        old=original[k]
        if old['text'] and old['text']!=v['text']:
            raise ValueError('Refusing to overwrite an already integrated or subsequently edited catalog: '+k)
    print('Drafted:',len(seen),'independently reviewed:',len(reviewed),'exclusions:',len(EXCLUDED),'meaning fixes:',len(fixes))
    print('Statuses:',dict(Counter(v['status'] for v in locale['messages'].values())))
    for k,v in list(locale['messages'].items())[:3]:print('SAMPLE',v['source'],'=>',v['text'])
    report={'source_catalog_sha256':locale['source_catalog_sha256'],'drafts':indexes,'reviews':review_indexes,
            'meaning_fixes':fixes,'translated_entries':len(seen),'independently_reviewed_entries':len(reviewed),
            'excluded_binary':list(EXCLUDED),'note':'Meaning proof applied before scripted naming. Original assets and story locales were not changed.'}
    return locale,report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--draft-only',action='store_true',help='Preflight drafts while independent proof is ongoing; never writes.')
    ap.add_argument('--write',action='store_true');args=ap.parse_args()
    if args.draft_only and args.write:raise ValueError('Draft-only preflight cannot write')
    locale,report=assemble(not args.draft_only)
    if args.write:
        LOCALE.write_bytes(encoded(locale).encode())
        (ROOT/'analysis/battle_review_index.json').write_bytes(encoded(report).encode())
    else:print('DRY RUN; --write integrates these reviewed drafts only.')


if __name__=='__main__':main()
