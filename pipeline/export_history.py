"""Past BDA auctions for the website's History page, built from every BDA lot on KPPP.
Usage: python export_history.py build/<id>/kppp_history.json ../web/public/data
Writes history.json: auction rounds (grouped by bidding date), per-locality outcomes and the full lot list."""
import json, os, statistics, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of, site_of, norm
from market import MARKET

src, root = sys.argv[1], sys.argv[2]
lots = json.load(open(src, encoding='utf8'))
# real final bids from BDA's archived result tables (fetch_results.py); KPPP itself never shows winning amounts or bidder counts
BIDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inputs', 'bid_results.json')
final = {(b['group'], norm(b['site'])): b for b in (json.load(open(BIDS, encoding='utf8')) if os.path.exists(BIDS) else []) if b['group']}
_KF2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inputs', 'kppp_finals.json')
_kf2 = json.load(open(_KF2, encoding='utf8')) if os.path.exists(_KF2) else {}
SOLD, UNSOLD = {'FINALIZED', 'BIDDING_CLOSED'}, {'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED'}
iso = lambda d: f'{d[6:10]}-{d[3:5]}-{d[0:2]}' if d else None

rows = []
for h in lots:
    d = iso(h.get('bidDate'))
    if not d: continue
    g = group_of(h['auctionTitle']); site = site_of(h['auctionTitle'])
    fb = final.get((g, site)) if h['statusKey'] in SOLD else None
    kf = _kf2.get((g + '|' + site)) if (g and site) else None   # real bid from signed-in collection (h1)
    real_final = (fb['final'] if fb else None) or (kf['h1'] if kf else None)
    real_src = (fb['auction'] if fb else None) or ('KPPP bid sheet' if kf else None)
    real_rej = kf.get('rejected') if kf else None
    real_nb = kf.get('bidderCount') if kf else None
    rows.append(dict(date=d, status=h['statusKey'], base=h.get('baseRate') or None, title=h['auctionTitle'].strip(),
                     no=h['auctionNoticeNumber'], group=g, locality=MARKET[g]['name'] if g in MARKET else ('Kempegowda Layout (NPKL)' if g == 'NPKL' else None), site=site,
                     reason=(h.get('recallReason') or '').strip() or None, cancelledOn=h.get('recalledOn'),
                     final=real_final, finalFrom=real_src, rejected=real_rej, bidderCount=real_nb))
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
# why lots were cancelled, grouped into plain categories
def why(r):
    t = (r or '').lower()
    return ('Court case' if 'court' in t else 'Forest / lake buffer' if ('forest' in t or 'buffer' in t or 'lake' in t) else
            'Already allotted' if 'allot' in t else 'Unavoidable circumstances' if 'unavoidable' in t else 'Other' if t else 'No reason given')
reasons = defaultdict(list)
for r in rows:
    if r['status'] == 'CANCELLED': reasons[why(r['reason'])].append(dict(date=r['date'], title=r['title'], no=r['no'], reason=r['reason'], locality=r['locality']))
import statistics as _st
_KF=os.path.join(os.path.dirname(os.path.abspath(__file__)),'inputs','kppp_finals.json')
_kf=json.load(open(_KF,encoding='utf8')) if os.path.exists(_KF) else {}
_v=[x for x in _kf.values() if x.get('h1')]
realBidStats=None
if _v:
    _prem=[(x['bidderCount'], round((x['h1']/x['base']-1)*100)) for x in _v if x.get('base')]
    _one=[pr for n,pr in _prem if n<=1]; _many=[pr for n,pr in _prem if n>=10]
    realBidStats=dict(sites=len(_v), rejectedPct=round(sum(1 for x in _v if x.get('rejected'))/len(_v)*100),
        oneBidderPct=round(sum(1 for x in _v if x['bidderCount']==1)/len(_v)*100),
        medianBidders=int(_st.median(x['bidderCount'] for x in _v)),
        tenPlus=sum(1 for x in _v if x['bidderCount']>=10),
        premOne=round(_st.median(_one)) if _one else None, premMany=round(_st.median(_many)) if _many else None,
        note='From real bid sheets collected for current-auction sites via a signed-in KPPP account, de-identified (counts and amounts only).')
json.dump(dict(rounds=out_rounds, lots=rows, cancellations=sorted(([k, v] for k, v in reasons.items()), key=lambda kv: -len(kv[1])),
          finalsKnown=sum(1 for r in rows if r['final']), realBidStats=realBidStats, summary=dict(lots=len(rows), sold=sum(r['status'] in SOLD for r in rows),
          unsold=sum(r['status'] in UNSOLD for r in rows), relistedSites=multi, uniqueSites=len(repeat),
          first=min(r['date'] for r in rows), last=max(r['date'] for r in rows)),
          note="KPPP shows each lot's outcome, base rate and cancellation reason, but not bid amounts or how many people took part. Final bids shown here come from BDA's own archived result tables (T-08, T-11)."),
          open(os.path.join(root, 'history.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('history: rounds', len(out_rounds), 'lots', len(rows))
