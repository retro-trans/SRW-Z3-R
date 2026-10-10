"""Keep GIFT notification text native until it reaches owned display storage."""
import re
from rengoku_runtime import require
from rengoku_screenshot_layout import line_width
from rengoku_category_layout import wrap

def spans(text):
 # Rengoku's extracted GIFT records are flat tuples, including the report
 # message and numeric gift metadata. They pass through bounded native slots.
 return [(m.start(),m.end()) for m in re.finditer(r'\bGIFT_\w+\s*=\s*\{[^{}]*\}',text)]

def hooks(row,codec):
 display=wrap(codec,row['english'],1050,32)
 jp=row['jp'].replace('\r\n','\n');js=jp.split('\n');es=display.split('\n')
 require(len(es)<=3,'Gift report exceeds notification panel')
 require(len(js)==len(es),'Gift report requires a separately verified line-count adapter')
 pairs={jp.encode('cp932'):codec.encode(display)}
 for a,b in zip(js,es):
  require(a and b,'Empty gift report fragment')
  pairs[a.encode('cp932')]=codec.encode(b)
 return pairs,dict(id=row['id'],display=display,native_source_retained=True,
     line_widths=[line_width(codec,s,32) for s in es],native_lines=len(js))
