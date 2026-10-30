"""Turn KPPP bid collections (private/kppp_bids.jsonl, from the user's signed-in account) into public, de-identified
per-site market facts: how many bid, the top bid amounts, and whether BDA rejected the result. No names, nicknames or IDs.
Usage: python ingest_kppp.py private/kppp_bids.jsonl inputs/kppp_finals.json"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of, site_of, norm

src, out = sys.argv[1], sys.argv[2]
recs = [json.loads(l) for l in open(src, encoding='utf8') if l.strip()] if os.path.exists(src) else []
iso = lambda d: f'{d[6:10]}-{d[3:5]}-{d[0:2]}' if d and len(d) >= 10 else None
finals = {}
for r in recs:
    g = group_of(r.get('title', '')); s = site_of(r.get('title', ''))
    if not (g and s): continue
    for lot in r.get('lots', []):
        bids = sorted(lot.get('bidders', []), key=lambda b: -(b.get('price') or 0))
        if not bids: continue
        prices = [b['price'] for b in bids if b.get('price')]
        statuses = [(b.get('status') or '').upper() for b in bids]
        date = iso(min((b.get('time', '') for b in bids), default='') .split()[0] if any(b.get('time') for b in bids) else None)
        rec = dict(base=lot.get('base'), reserve=lot.get('reserve'), status=lot.get('status'),
                   bidderCount=len(bids), h1=prices[0] if prices else None, h2=prices[1] if len(prices) > 1 else None,
                   h3=prices[2] if len(prices) > 2 else None, allPrices=prices,
                   rejected=all('REJECT' in x for x in statuses) if statuses and any(statuses) else None,
                   topRejected='REJECT' in (statuses[0] if statuses else ''), date=date, source='KPPP (bidder view)')
        if lot.get('base') and rec['h1']:
            rec['premium'] = round((rec['h1'] / lot['base'] - 1) * 100, 1)
        finals[f'{g}|{norm(s)}'] = rec   # last collection wins (newest round)
json.dump(finals, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('kppp finals:', len(finals), '| rejected:', sum(1 for v in finals.values() if v.get('rejected')))
