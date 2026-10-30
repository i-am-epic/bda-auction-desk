"""One spreadsheet of every past BDA lot on KPPP, with every public field and the real final bid where one is known.
Usage: python export_lots_csv.py build/<id>/kppp_history_full.json inputs/bid_results.json ../exports/bda_kppp_lot_history.csv"""
import csv, json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of, site_of, norm
from market import MARKET

hist_p, bids_p, out_p = sys.argv[1:4]
lots = json.load(open(hist_p, encoding='utf8'))
bids = json.load(open(bids_p, encoding='utf8'))
SQ = 10.7639
OUTCOME = {'FINALIZED': 'Sold / closed with a result', 'BIDDING_CLOSED': 'Bidding closed', 'NO_PARTICIPATIONS': 'No bidders',
           'NO_BIDS_RECEIVED': 'No bids', 'CANCELLED': 'Cancelled', 'EVALUATED': 'Evaluated', 'UNDER_EVALUATION': 'Under evaluation'}
name = lambda g: MARKET[g]['name'] if g in MARKET else ('Kempegowda Layout (NPKL)' if g == 'NPKL' else '')
ymd = lambda d: f'{d[6:10]}-{d[3:5]}-{d[0:2]}' if d else ''

final = {}   # (group, site) -> real final bid from archived result tables
for b in bids:
    if b['group']: final[(b['group'], norm(b['site']))] = b

for l in lots:
    l['_g'] = group_of(l['auctionTitle']); l['_s'] = site_of(l['auctionTitle']); l['_d'] = ymd(l.get('bidDate'))
lots.sort(key=lambda l: (l['_d'], l['auctionNoticeNumber']))
seen = defaultdict(list)
rows = []
for l in lots:
    k = (l['_g'], l['_s'])
    prev = seen[k]
    fb = final.get(k) if l['statusKey'] in ('FINALIZED', 'BIDDING_CLOSED') else None
    base = l.get('baseRate') or None
    rows.append([l['auctionNoticeNumber'], l['auctionNoticeId'], l['auctionTitle'].strip(), name(l['_g']), l['_s'] or '',
                 OUTCOME.get(l['statusKey'], l['statusKey']), l['_d'], (l.get('bidEnd') or '')[11:16], l.get('deltaMin') or '',
                 ymd(l.get('eoiDeadline')), ymd((l.get('auctionPublishedDate') or '')[:10]),
                 int(base) if base else '', round(base / SQ) if base else '', int(l['emd']) if l.get('emd') else '', int(l['fee']) if l.get('fee') else '',
                 len(prev), prev[-1] if prev else '', l.get('recallReason') or '', l.get('recalledOn') or '',
                 int(fb['final']) if fb else '', round(fb['final'] / SQ) if fb else '', round((fb['final'] / fb['base'] - 1) * 100, 1) if fb else '',
                 fb['area'] if fb else '', fb['auction'] if fb else '',
                 f"https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/{l['auctionNoticeId']}/view-auction"])
    seen[k].append(OUTCOME.get(l['statusKey'], l['statusKey']))
rows.reverse()   # newest first
os.makedirs(os.path.dirname(out_p), exist_ok=True)
with open(out_p, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Auction no.', 'KPPP id', 'Title', 'Locality', 'Site no.', 'Outcome', 'Bid date', 'Bidding closed at', 'Extension (min)',
                'Interest deadline', 'Published', 'Base Rs/m2', 'Base Rs/ft2', 'EMD Rs', 'Fee Rs', 'Times listed before', 'Previous outcome',
                'Cancel reason', 'Cancelled on', 'Real final bid Rs/m2', 'Real final bid Rs/ft2', 'Final over base %', 'Area m2 (from result table)',
                'Result table', 'KPPP record (JSON)'])
    w.writerows(rows)
print('rows', len(rows), 'with real final bid', sum(1 for r in rows if r[19] != ''), '->', out_p)
