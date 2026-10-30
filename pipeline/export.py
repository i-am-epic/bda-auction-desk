"""Export the analysed auction into the website's data files.
Usage: python export.py build/data2.json ../web/public/data
Writes sites.json (one record per site, trimmed for the browser) and meta.json (auction facts, locality history)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from market import MARKET

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
pack = json.load(open(src, encoding='utf8'))
sites, hist = pack['sites'], pack['history']

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', f"{s['sl']}-{s['site']}".lower()).strip('-')

def r6(p): return [round(p[0], 6), round(p[1], 6)]

KEEP = ['sl', 'site', 'layout', 'zone', 'group', 'locality', 'source', 'status', 'ew', 'ns', 'area', 'area_corr', 'areaSqft', 'rate',
        'ratePerSqft', 'baseTotal', 'minBidRate', 'minBidTotal', 'expRate', 'expTotal', 'expLo', 'expHi', 'expPremium', 'maxBidRate',
        'maxBidTotal', 'fairRate', 'fairLo', 'fairHi', 'fairSqft', 'fairTotal', 'marketSqft', 'upside', 'headroomAtExp', 'premiumOverBase',
        'valueBasis', 'competition', 'compLabel', 'bidders', 'winChance', 'noBidRisk', 'stampReg', 'tds', 'allIn', 'buildCost',
        'projectCost', 'builtUpSqft', 'floors', 'far', 'use', 'rentMonthly', 'rentalYield', 'commercialYield', 'resaleReturn', 'value5y',
        'gain5y', 'score', 'scoreParts', 'verdict', 'greatFind', 'sleeper', 'flags', 'surroundRisks', 'surroundGoods', 'vastu',
        'findings', 'description', 'personas', 'pros', 'cons', 'kppp', 'prevRounds', 'prevBase', 'baseChange', 'marketCap', 'commercial',
        'road', 'metro', 'hubs', 'growth', 'projects', 'geotag', 'geoNote', 'polyArea', 'polyDrawn', 'irregularity', 'usability', 'tier']
rows = []
for s in sites:
    r = {k: s.get(k) for k in KEEP}
    r['id'] = slug(s)
    r['lat'], r['lon'] = round(s['lat'], 6), round(s['lon'], 6)
    r['polygon'] = [r6(p) for p in s['polygon']]
    g = s.get('geo') or {}
    r['terrain'] = dict(elev=g.get('elev'), slope=g.get('slope'), aspect=g.get('aspect'), relief=g.get('relief'), facing=g.get('facing'),
                        frontage=(g.get('frontage') or {}).get('name') or ((g.get('frontage') or {}).get('tags') or {}).get('highway'),
                        frontageM=(g.get('frontage') or {}).get('m'))
    r['near'] = {k: dict(m=v['m'], name=v.get('name') or '') for k, v in (g.get('near') or {}).items()}
    r['bidDay'] = None if s['sl'].startswith('C') else ('2026-11-02' if int(s['sl']) <= 46 else '2026-11-03' if int(s['sl']) <= 92 else '2026-11-04')
    rows.append(r)

groups = {}
for g, m in MARKET.items():
    members = [r for r in rows if r['group'] == g]
    if not members: continue
    act = [r for r in members if r['status'] == 'active']
    groups[g] = dict(id=g.lower(), name=m['name'], lo=m['lo'], mid=m['mid'], hi=m['hi'], tier=m['tier'], cagr=m['cagr'], growth=m['growth'],
                     demand=m['demand'], ask=m['ask'], story=m['story'], drivers=m['drivers'], watch=m['watch'],
                     history=hist.get(g), projects=members[0]['projects'], sites=len(act),
                     center=[sum(r['lat'] for r in members)/len(members), sum(r['lon'] for r in members)/len(members)],
                     bestScore=max((r['score'] or 0) for r in act) if act else None,
                     baseRates=sorted({r['rate'] for r in act}))

meta = dict(
    auction=dict(code='T-15', notice='BDA/EM/e-Auction/T-15/2026-27', noticeDate='2026-10-03', eoiDeadline='2026-10-31T17:00:00+05:30',
                 bidDays=[dict(date='2026-11-02', range='Sl 1-46'), dict(date='2026-11-03', range='Sl 47-92'), dict(date='2026-11-04', range='Sl 93-138')],
                 emd=400000, fee=500, notice_pdf='https://www.bdakarnataka.in/api/media/e-auction/pdf_press_release/e_auction-12102026_1791186164533_0e517992.pdf',
                 corrigendum_pdf='https://www.bdakarnataka.in/api/media/e-auction/pdf_press_release/1574_BDA_corrigendum_(1)-1_1792750776940_04ea4c26.pdf',
                 kppp='https://kppp.karnataka.gov.in/#/portal/Auctions/live', helpline='9483166622'),
    generated='2026-10-30', groups=groups,
    calibration=dict(note='Expected bids calibrated to BDA Dec 2021: 296 sites sold for ~Rs 348 cr against ~Rs 215 cr base (+62%); corner sites +44%.',
                     src='https://thebengalurulive.com/bdas-e-auction-of-bengaluru-sites-nets-rs-411-59-crore/'),
)
json.dump(rows, open(os.path.join(out, 'sites.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
json.dump(meta, open(os.path.join(out, 'meta.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('sites', len(rows), os.path.getsize(os.path.join(out, 'sites.json')), 'groups', len(groups))
