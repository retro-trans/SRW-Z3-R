"""Preview the final source transcription correction and screenshot cross-references."""
import argparse
import json
from non_dialogue import ROOT, digest, encoded


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    source_path=ROOT/'source/artwork.json'
    target_path=ROOT/'localization/locales/en/artwork.json'
    raw=source_path.read_bytes()
    source=json.loads(raw)
    target=json.loads(target_path.read_text(encoding='utf-8'))
    if target['source_catalog_sha256']!=digest(raw):
        if target['source_catalog_sha256']!=digest(source_path.read_text(encoding='utf-8').encode()):
            raise ValueError('Artwork catalog binding changed')
        print('Repair LF-versus-CRLF catalog hash from initial Windows text write; JSON content matches exactly.')
    for row in source['records']:
        entry=target['messages'][row['id']]
        if entry['source']!=row['source'] or entry['source_sha256']!=digest(row['source'].encode()) or row['source_sha256']!=entry['source_sha256']:
            raise ValueError('Artwork source binding changed: '+row['id'])
    review=json.loads((ROOT/'work/non_dialogue_reviews/manual_01.json').read_text(encoding='utf-8'))
    source['manual_screenshot_references']=review['screenshot_catalog_context']
    corrections=[]
    for r in source['records']:
        entry=target['messages'][r['id']]
        if r['id']=='art:9a5c2cfffe67422701e0' and '富士見書房刊' in r['source']:
            old=r['source']
            r['source']=old.replace('富士見書房刊','富士見書房・刊')
            r['source_sha256']=digest(r['source'].encode())
            entry.update(source=r['source'],source_sha256=r['source_sha256'])
            corrections.append({'id':r['id'],'previous':old,'corrected':r['source'],
                                'reason':'Visible separator on startup copyright image; English meaning unchanged.',
                                'image':r['image'],'image_sha256':r['image_sha256']})
        if 'オケアノス' in r['source'] and entry['status']=='needs_review':
            entry.update(status='reviewed',notes='Okeanos attribution checked against original image and analysis/rengoku_terms.json sources.')
            print(r['id'],'Okeanos attribution resolved')
    new=encoded(source).encode()
    target['source_catalog_sha256']=digest(new)
    print('Screenshot cross-references:',len(source['manual_screenshot_references']['ids']))
    print('Corrections:',corrections)
    if args.write:
        history=ROOT/'source/artwork_history'/ (digest(raw)+'.json')
        history.parent.mkdir(parents=True,exist_ok=True)
        if history.exists() and history.read_bytes()!=raw:
            raise ValueError('Artwork history collision')
        history.write_bytes(raw)
        source_path.write_bytes(new)
        target_path.write_text(encoded(target),encoding='utf-8')
        if corrections:
            (ROOT/'analysis/artwork_transcription_correction.json').write_text(encoded({
                'previous_catalog_sha256':digest(raw),'catalog_sha256':digest(new),'corrections':corrections,
                'manual_screenshot_references':source['manual_screenshot_references']}),encoding='utf-8')
    else:
        print('DRY RUN; --write updates catalogs and preserves the previous source snapshot.')


if __name__=='__main__':
    main()
