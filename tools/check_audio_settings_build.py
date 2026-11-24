"""Read-only verification of packed audio/settings captions and geometry."""
import argparse,json
from pathlib import Path
from cpk import CPK
from rengoku_runtime import require
from rengoku_search_layout import field

def check(build):
    build=Path(build)
    report=json.loads((build/'BUILD_REPORT.json').read_text(encoding='utf8'))
    def encode(text):
        return b''.join(bytes.fromhex(report['font_mapping'][c]['cp932'])
            if c in report['font_mapping'] else c.encode('cp932') for c in text)
    archive=CPK(str(build/'RPCS3/NPJB00689/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'))
    packed=archive.read(next(e for e in archive.files if e['id']==0))
    original=CPK(str(Path(__file__).resolve().parents[1]/'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'))
    source=original.read(next(e for e in original.files if e['id']==0))
    rows=report['audio_settings_layout'];require(len(rows)==36,'Missing settings proof rows')
    for item in rows:
        row=int(item['row'],16)
        require(field(source,row)==item['source'].encode('cp932'),'Original settings source mismatch')
        require(field(packed,row)==encode(item['display']),'Packed settings caption mismatch')
        require(packed[row+4:row+32]==source[row+4:row+32],'Native control layout changed')
        require(max(item['line_widths'],default=0)<=item['width_limit'],'Recorded settings bounds exceeded')
    for row in (0x94544,0x945e4,0x94644,0x946e4,0x94d64):
        require(packed[row+4:row+32]==source[row+4:row+32],'Option position/style changed')
        require(field(packed,row)==field(source,row),'Native option text changed')
    for row,text in ((0x94704,'Main'),(0x94724,'Single')):
        require(packed[row+4:row+32]==source[row+4:row+32],'Option position/style changed')
        require(field(packed,row)==encode(text),'Existing option translation changed')
    result=dict(version=report['version'],packed_caption_readbacks=len(rows),
        caption_geometry_and_style_preserved=True,native_options_preserved=True,
        gameplay_tested=False,all_passed=True)
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path)
    check(p.parse_args().build)
