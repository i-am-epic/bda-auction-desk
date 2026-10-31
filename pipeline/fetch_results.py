"""Real BDA winning bids. bdaeauction.in archives closed BDA notifications (T-08, T-09, T-11, ...) with a "Final Bid (Rs/Sq.Mtr)" column.
KPPP itself does not publish winning amounts, so this is the only per-lot source of final prices we have found.
Usage: python fetch_results.py inputs/bid_results.json [saved.html]   (downloads the page when no saved copy is given)"""
import html, json, re, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of

out = sys.argv[1]
if len(sys.argv) > 2:
    page = open(sys.argv[2], encoding='utf8').read()
else:
    page = subprocess.run(['curl', '-sSL', '-m', '120', '-A', 'Mozilla/5.0', 'https://www.bdaeauction.in/'],
                          capture_output=True, text=True, encoding='utf8').stdout
num = lambda t: float(re.sub(r'[^\d.]', '', t) or 0)
clean = lambda x: html.unescape(re.sub(r'<[^>]+>', ' ', x)).strip()

def avg(e):
    e = e.replace('[', '(').replace(']', ')').strip(); e = re.sub(r'\)\s*2$', ')/2', e)
    try: return float(eval(e, {'__builtins__': {}})) if re.fullmatch(r'[0-9.+*/() ]+', e) else None
    except Exception: return None

lots = []
for t in re.finditer(r'<table[^>]*>(.*?)</table>', page, re.S):
    body = t.group(1)
    heads = [clean(h) for h in re.findall(r'<th[^>]*>(.*?)</th>', body, re.S)]
    if not any('Final Bid' in h for h in heads): continue
    col = {h: i for i, h in enumerate(heads)}
    fi = next(i for h, i in col.items() if 'Final Bid' in h)
    bi = next(i for h, i in col.items() if 'Initial Bid' in h and 'Mtr' in h)
    ai = next(i for h, i in col.items() if 'Area' in h and 'Mtr' in h)
    di = next((i for h, i in col.items() if h.startswith('Dimension')), None)
    # the notification code is in the text just before the table
    code = (re.findall(r'T-(\d{2})/20\d\d-\d\d', page[max(0, t.start() - 20000):t.start()]) or ['?'])[-1]
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', body, re.S):
        c = [clean(x) for x in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
        if len(c) <= max(fi, bi, ai): continue
        base, final, area = num(c[bi]), num(c[fi]), num(c[ai])
        if not (base and final and area): continue
        layout = re.sub(r'^(North|South|West|East)\s+', '', c[1]).replace(' — ', ', ')
        ew = ns = None
        if di is not None and '×' in c[di]:
            ew, ns = [avg(x.replace('m', '').strip()) for x in c[di].split('×')[:2]]
        lots.append(dict(auction=f'T-{code}', layout=layout, site=c[2], area=area, base=base, final=final, ew=ew, ns=ns,
                         group=group_of(f'Site No-{c[2]} at {layout}')))
# Guard: bdaeauction.in occasionally serves a page the parser reads as 0 rows (layout change / rate limit).
# Never overwrite a good archive with an empty scrape; keep the last known-good file instead.
if not lots and os.path.exists(out):
    prev = json.load(open(out, encoding='utf8'))
    print('final bids: 0 scraped — keeping existing', len(prev), 'records (empty scrape ignored)')
else:
    json.dump(lots, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    from collections import Counter
    print('final bids:', len(lots), Counter(l['auction'] for l in lots), 'in our localities:', sum(1 for l in lots if l['group'] and l['group'] != 'NPKL'))
