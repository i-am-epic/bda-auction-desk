"""Past BDA auctions for the website's History page, built from every BDA lot on KPPP.
Usage: python export_history.py build/<id>/kppp_history.json ../web/public/data
Writes history.json: auction rounds (grouped by bidding date), per-locality outcomes and the full lot list."""
import json, os, statistics, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of, site_of
from market import MARKET

src, root = sys.argv[1], sys.argv[2]
lots = json.load(open(src, encoding='utf8'))
SOLD, UNSOLD = {'FINALIZED', 'BIDDING_CLOSED'}, {'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED'}
iso = lambda d: f'{d[6:10]}-{d[3:5]}-{d[0:2]}' if d else None

rows = []
for h in lots:
    d = iso(h.get('bidDate'))
    if not d: continue
    g = group_of(h['auctionTitle'])
    rows.append(dict(date=d, status=h['statusKey'], base=h.get('baseRate') or None, title=h['auctionTitle'].strip(),
                     no=h['auctionNoticeNumber'], group=g, locality=MARKET[g]['name'] if g in MARKET else ('Kempegowda Layout (NPKL)' if g == 'NPKL' else None), site=site_of(h['auctionTitle'])))
rows.sort(key=lambda r: (r['date'], r['no']), reverse=True)

# a "round" = all lots bid in the same calendar month (BDA runs one notification across a few consecutive days)
rounds = defaultdict(list)
for r in rows: rounds[r['date'][:7]].append(r)
out_rounds = []
for m, rs in sorted(rounds.items(), reverse=True):
    bases = [r['base'] for r in rs if r['base']]
    by_loc = defaultdict(lambda: [0, 0])
    for r in rs:
        if r['locality']: by_loc[r['locality']][0 if r['status'] in SOLD else 1] += r['status'] in SOLD | UNSOLD
    out_rounds.append(dict(month=m, start=min(r['date'] for r in rs), end=max(r['date'] for r in rs), lots=len(rs),
        sold=sum(r['status'] in SOLD for r in rs), unsold=sum(r['status'] in UNSOLD for r in rs), cancelled=sum(r['status'] == 'CANCELLED' for r in rs),
        upcoming=sum(r['status'] not in SOLD | UNSOLD | {'CANCELLED'} for r in rs),
        medianBase=round(statistics.median(bases)) if bases else None, minBase=min(bases) if bases else None, maxBase=max(bases) if bases else None,
        localities=sorted(([k, v[0], v[1]] for k, v in by_loc.items()), key=lambda x: -(x[1] + x[2]))[:8]))

# how often the same site comes back
repeat = defaultdict(list)
for r in rows:
    if r['group'] and r['site']: repeat[(r['group'], r['site'])].append(r)
multi = sum(1 for v in repeat.values() if len(v) > 1)
json.dump(dict(rounds=out_rounds, lots=rows, summary=dict(lots=len(rows), sold=sum(r['status'] in SOLD for r in rows),
          unsold=sum(r['status'] in UNSOLD for r in rows), relistedSites=multi, uniqueSites=len(repeat),
          first=min(r['date'] for r in rows), last=max(r['date'] for r in rows)),
          note='KPPP shows each lot\'s outcome and base rate but not the winning amount.'),
          open(os.path.join(root, 'history.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('history: rounds', len(out_rounds), 'lots', len(rows))
