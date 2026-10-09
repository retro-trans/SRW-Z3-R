"""Build source-bound English artwork drafts, without modifying raster originals."""
import argparse
import json
from pathlib import Path
from non_dialogue import ROOT, LOCALE, digest, encoded


def build():
    manifest = {}
    for path in (ROOT/'work/artwork').glob('*/manifest.json'):
        for row in json.loads(path.read_text(encoding='utf-8')):
            manifest[row['image']] = row
    source, messages = [], {}
    def add(image, label, jp, en, status='draft', notes=None):
        image = 'work/artwork/'+image if not image.startswith('work/') else image
        meta = manifest[image]
        identity = 'art:'+digest((image+'::'+label).encode())[:20]
        row = {'id': identity, 'asset': meta['asset'], 'asset_sha256': meta['sha256'], 'image': image,
               'image_sha256': digest((ROOT/image).read_bytes()), 'region': label, 'source': jp,
               'source_sha256': digest(jp.encode()), 'texture': meta['texture'], 'frame': meta['frame']}
        source.append(row)
        messages[identity] = {'source': jp, 'text': en, 'status': status, 'source_sha256': row['source_sha256']}
        if notes:
            messages[identity]['notes'] = notes
    manual_path = ROOT/'work/batches/manual_01_authored.json'
    manual = json.loads(manual_path.read_text(encoding='utf-8'))
    review = json.loads((ROOT/'work/non_dialogue_reviews/manual_01.json').read_text(encoding='utf-8'))
    if digest(manual_path.read_bytes()) != review['draft_sha256']:
        raise ValueError('Manual proof snapshot changed')
    copyright_pair = None
    for page in manual['pages']:
        for label, jp, en in page['blocks']:
            fix = review['fixes'].get(page['asset']+'::'+label)
            status = 'reviewed'
            if fix:
                if fix['source'] != jp or fix['previous'] != en:
                    raise ValueError('Stale manual proof')
                jp, en, status = fix['corrected_source'], fix['text'], fix['status']
            add(page['image'], label, jp, en, status)
            if label == 'cover copyright':
                copyright_pair = (jp, en)
    def atlas(image, pairs, note=None):
        for n, (jp, en) in enumerate(pairs):
            add(image, 'label %02d: %s' % (n+1, jp), jp, en, notes=note)
    atlas('aid/1_0_0.png', [
        ('シールド防御','Shield Defense'),('切り払い','Sword Parry'),('分身','Afterimage'),('バリア','Barrier'),
        ('出撃不可','Cannot Deploy'),('合体','Combine'),('インターミッション','Intermission'),('サブオーダー','Sub Order'),
        ('鉄','Guard'),('幸','Luck'),('集','Focus'),('努','Gain'),('必','Strike'),('乱','Disrupt'),('加','Accel'),('分','Analyze'),('覚','Zeal')],
        'Single-kanji tiles are Spirit Command icons, not ordinary prose. Full English drafts; tile layout needs rebuilding.')
    atlas('aid/1_2_0.png', [
        ('全体','ALL'),('攻撃','Attack'),('センター','Center'),('ワイド','Wide'),('マップ','MAP'),
        ('マキシマム','Maximum'),('ブレイク','Break'),('カウンター','Counter'),('援護','Support'),('攻撃','Attack'),('防御','Defend'),
        ('再','Re-'),('兵器','Weapon'),('歌','Song'),('精神','Spirit'),('付与','Grant'),('運動','Mobility'),('気力','Focus'),
        ('照準','Accuracy'),('能力','Ability'),('装甲','Armor'),('戦闘','Battle'),('回復','Recovery'),('性','Property'),
        ('上昇','Increase'),('値','Value'),('半減','Halved'),('最大','Maximum'),('低下','Decrease'),('不能','Disabled'),('コマンド','Command'),
        ('ゲーム','Game'),('スタート','Start'),('データをリンクさせて','Link Data and'),('主人公設定','Protagonist Setup'),
        ('シナリオ選択','Scenario Select'),('本編','Main Story'),('ガイダンス','Guidance'),('シナリオ','Scenario')],
        'Atlas fragments are combined at runtime. Translate the composed label when rebuilding; do not replace tiles independently.')
    atlas('aid/1_3_0.png', [('単','Single'),('合体','Combine'),('出撃不可','Cannot Deploy'),('機','Unit'),('合体攻撃','Combination Attack'),('魂','Soul')])
    for image, pairs in [('tpack/2_1_0.png', [('援護 1','Support 1'),('援護 2','Support 2'),('援護 3','Support 3'),('援護 4','Support 4')]),
                         ('tpack/2_4_0.png', [('搭載','Aboard')]),('tpack/2_5_0.png',[('マルチアクション','Multi Action')]),
                         ('battle_ui/0_41952-10_0.png',[('合体攻撃','Combination Attack')]),
                         ('battle_ui/0_41952-11_0.png',[('カウンター','Counter'),('再攻撃','Re-Attack'),('援護攻撃','Support Attack'),('援護防御','Support Defend')]),
                         ('battle_ui/0_41952-16_0.png',[('マキシマムブレイク','Maximum Break')])]:
        atlas(image,pairs)
    titles = ['翠の地球','乙女の祈り','駆け抜ける獅子','天秤の皿の上','スフィアを追う者','脱走者','ターミナル・ベース攻防戦','尸魂の徒','悲しみの乙女、再び',
              '傷だらけの獅子、荒野に吼える','揺れる天秤、揺れない意志','誓いの決戦','迫る猛毒','時の牢獄で','死闘の果てに']
    locale = json.loads(LOCALE.read_text(encoding='utf-8'))['messages']
    for i, jp in enumerate(titles,4):
        choices = [(k,v) for k,v in locale.items() if v['source'].replace('\u3000','').strip() == jp and v['text']]
        if len({v['text'] for k,v in choices}) != 1:
            raise ValueError('Ambiguous chapter title: '+jp)
        add('tpack/%d_0_0.png'%i,'chapter title, normal and glow copies',jp,choices[0][1]['text'],notes='Same chapter heading as '+choices[0][0])
    title = '第３次スーパーロボット大戦Ｚ　連獄篇'
    for image in ['manual/ICON0_0_0.png']+['kdata/%d_0_0.png'%i for i in range(3)]:
        add(image,'game title logo',title,'Super Robot Wars Z3: Rengoku-hen')
    add('tpack_extra/0_0-0_0.png','heading','ご注意','Notice')
    add('tpack_extra/0_0-0_0.png','body',
        'ゲームソフトを権利者の許諾なく、インターネットを通じて配信、配布する行為、また、違法なインターネット配信と知りながらダウンロードする行為は法律で固く禁じられております。\nみなさまのご理解とご協力をお願いいたします。',
        'Distributing game software over the Internet without permission from the rights holder, or knowingly downloading an illegally distributed copy, is strictly prohibited by law.\nThank you for your understanding and cooperation.')
    # Each startup owner appears in the already proofread manual copyright block.
    jps = [part for line in copyright_pair[0].splitlines() for part in line.split('\u3000')]
    ens = [part for line in copyright_pair[1].splitlines() for part in line.split('\u3000')]
    jps[8:10] = [' '.join(jps[8:10])]
    ens[8:10] = [' '.join(ens[8:10])]
    if len(jps) != 23 or len(ens) != 23:
        raise ValueError('Copyright column mismatch')
    for i,(jp,en) in enumerate(zip(jps,ens)):
        jp=jp.replace('富士見書房刊','富士見書房・刊')
        image = 'tpack_extra/0_%d-0_0.png' % (11059584 if i<11 else 14746112)
        add(image,'copyright line %d'%(i+1 if i<11 else i-10),jp,en,'needs_review' if i==0 else 'reviewed',
            'Transcribed from startup image; same ownership attribution as manual. Preserve historical wording.')
    output = {'schema':1,'records':source,'manual_screenshot_references':review['screenshot_catalog_context'],
              'limits':['English drafts only; original raster assets are unchanged.', 'Region labels identify text visually, not insertion positions.', 'Font glyph atlases are character resources and are excluded.']}
    local = {'schema':1,'language':'en','source_catalog_sha256':digest(encoded(output).encode()),'messages':messages}
    return output,local


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    source,locale=build()
    print('Artwork text blocks:',len(source['records']))
    for row in source['records'][64:]:
        print(row['image'],row['region'],repr(row['source']),'=>',repr(locale['messages'][row['id']]['text']))
    if args.write:
        for path,content in [(ROOT/'source/artwork.json',source),(ROOT/'localization/locales/en/artwork.json',locale)]:
            if path.exists():
                raise ValueError('Refusing existing catalog: '+str(path))
        (ROOT/'source/artwork.json').write_bytes(encoded(source).encode())
        (ROOT/'localization/locales/en/artwork.json').write_text(encoded(locale),encoding='utf-8')
    else:
        print('DRY RUN; --write creates new catalogs only.')


if __name__=='__main__':
    main()
