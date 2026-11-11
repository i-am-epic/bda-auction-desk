"""Auto-fetch an auction's inputs so no row is transcribed by hand.

Two public sources, joined:
  1. BDA geotag map (http://106.51.29.213/ by default) — its page embeds a GeoJSON FeatureCollection with
     Sl_No, Site_No, Layout, East_to_We, North_to_S, Area_(Sq._, Division + the plot polygon. That is every
     column the notice table has, plus the geometry.
  2. KPPP public auction-search / view-auction — the base rate (Rs/sq m), bid dates and notice number per lot,
     which the geotag does not carry.

Output: auctions/<id>/geotag.json (the FeatureCollection) and a ready ROWS block + AUCTION base facts printed
for notice.py. Site numbers are not unique across layouts, so geotag and KPPP are joined on (Site_No, group).

Usage:
  python fetch_bda.py <id>                         # geotag from http://106.51.29.213/, bases from KPPP
  python fetch_bda.py <id> http://106.51.29.213/   # explicit geotag URL (per-auction map link also works)
"""
import json, os, re, subprocess, sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of

HERE = os.path.dirname(os.path.abspath(__file__))
KAPI = 'https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service'
NL = chr(10)
norm = lambda s: re.sub(r'[^0-9A-Z]', '', str(s or '').upper())


def fetch_geotag(url):
    """Pull the inline GeoJSON FeatureCollection out of the BDA geotag map page."""
    html = subprocess.run(['curl', '-sSL', '-m', '90', url], capture_output=True, text=True, encoding='utf8', errors='replace').stdout
    i = html.find('FeatureCollection')
    if i < 0:
        raise SystemExit(f'no FeatureCollection found at {url}')
    start = html.rfind('{', 0, i)
    depth = 0
    for j in range(start, len(html)):
        if html[j] == '{': depth += 1
        elif html[j] == '}':
            depth -= 1
            if depth == 0:
                return json.loads(html[start:j + 1])
    raise SystemExit('FeatureCollection braces did not balance')


def prop(p, *names):
    """Geotag property keys are truncated (e.g. 'Area_(Sq._'); match by prefix, case-insensitive."""
    for n in names:
        for k, v in p.items():
            if k.lower().startswith(n.lower()): return v
    return None


def kppp_search(status, word, page=0):
    r = subprocess.run(['curl', '-s', '-m', '40', '-D', '-', '-X', 'POST', f'{KAPI}/search/auction-search?page={page}&pageSize=10',
                        '-H', 'Content-Type: application/json', '-d', json.dumps({'auctionStatus': status, 'auctionTitle': word})],
                       capture_output=True, text=True, encoding='utf8')
    head, _, body = r.stdout.partition(NL + NL)
    total = next((int(l.split(':')[1]) for l in head.splitlines() if l.lower().startswith('x-total-count')), 0)
    try: return json.loads(body or '[]'), total
    except Exception: return [], total


def kppp_base_index(words, statuses):
    """{(Site_No_norm, group): {base, no, id, bidStart, eoi}} across the given statuses and locality words."""
    lots = {}
    for st in statuses:
        for w in words:
            rows, total = kppp_search(st, w)
            pages = [rows] + list(ThreadPoolExecutor(6).map(lambda p: kppp_search(st, w, p)[0], range(1, (total + 9) // 10)))
            for rs in pages:
                for a in rs:
                    if a['auctionNoticeNumber'].startswith('BDA/'): lots[a['auctionNoticeId']] = a
    def detail(a):
        b = subprocess.run(['curl', '-s', '-m', '30', f"{KAPI}/{a['auctionNoticeId']}/view-auction"], capture_output=True, text=True, encoding='utf8').stdout
        try:
            d = json.loads(b); n = d['auctionNoticeDTO']; slot = (d.get('auctionBiddingSlotDTO') or [{}])[0]
            sch = ((d.get('auctionScheduleInformationDTO') or {}).get('auctionSchedule') or {})
            site = re.search(r'Site No-?\s*([0-9A-Za-z/]+)', a['auctionTitle'])
            a['_site'] = site.group(1) if site else ''
            a['_base'] = float(n.get('totalAmount') or 0); a['_start'] = slot.get('auctionStartDate'); a['_eoi'] = sch.get('auctionParticipationInterestDate')
            a['_emd'] = sch.get('fullEmd'); a['_fee'] = sch.get('auctionFee')
        except Exception:
            a['_base'] = None
        return a
    idx = {}
    dkey = lambda s: tuple(int(x) for x in reversed((s or '01-01-1900 00:00:00').split()[0].split('-')))  # dd-mm-yyyy -> sortable
    # oldest first, so the newest round for a (site, group) overwrites it
    for a in sorted(ThreadPoolExecutor(8).map(detail, lots.values()), key=lambda a: dkey(a.get('_start'))):
        g = group_of(a['auctionTitle'])
        if a.get('_base'):
            idx[(norm(a.get('_site')), g)] = dict(base=a['_base'], no=a['auctionNoticeNumber'], id=a['auctionNoticeId'], bidStart=a.get('_start'), eoi=a.get('_eoi'), emd=a.get('_emd'), fee=a.get('_fee'))
    return idx


def build(aid, geo_url):
    gj = fetch_geotag(geo_url)
    feats = gj['features']
    words = sorted({group_of(prop(f['properties'], 'Layout')) or '' for f in feats})
    # locality keywords to search KPPP with (cover the groups present)
    kw = sorted({w for f in feats for w in re.findall(r'[A-Za-z]{5,}', prop(f['properties'], 'Layout') or '')
                 if w.upper() in ('BANASHANKARI', 'ANJANAPURA', 'ARKAVATHI', 'ARKAVATHY', 'VISHVESHWARAH', 'VISHWESHWARAIAH', 'NAGAR', 'KEMPEGOWDA', 'NADAPRABHU')})
    bases = kppp_base_index(kw or ['BANASHANKARI'], ['PUBLISHED', 'LIVE_AUCTION', 'BIDDING_CLOSED', 'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED', 'UNDER_EVALUATION', 'EVALUATED', 'FINALIZED'])
    rows, matched = [], 0
    for f in feats:
        p = f['properties']; g = group_of(prop(p, 'Layout'))
        site = str(prop(p, 'Site_No') or '').strip()
        b = bases.get((norm(site), g))
        if b: matched += 1
        rows.append('|'.join([str(prop(p, 'Sl_No') or ''), site, str(prop(p, 'Layout') or '').strip(),
                              str(prop(p, 'East_to_We') or ''), str(prop(p, 'North_to_S') or ''),
                              str(prop(p, 'Area_(Sq._', 'Area') or ''), str(int(b['base']) if b else '') , str(prop(p, 'Division') or 'South'), g or '?']))
    out = os.path.join(HERE, 'auctions', aid)
    os.makedirs(out, exist_ok=True)
    json.dump(gj, open(os.path.join(out, 'geotag.json'), 'w', encoding='utf8'), ensure_ascii=False)
    any_b = next(iter(bases.values()), {})
    print(f'geotag: {len(feats)} sites -> auctions/{aid}/geotag.json')
    print(f'KPPP base rates matched: {matched}/{len(feats)}  (groups: {sorted(set(r.split("|")[-1] for r in rows))})')
    if any_b: print(f'auction facts from KPPP — EOI {any_b.get("eoi")}, bidStart {any_b.get("bidStart")}, EMD {any_b.get("emd")}, fee {any_b.get("fee")}')
    print('--- ROWS (paste into auctions/%s/notice.py) ---' % aid)
    print('ROWS = """')
    print(NL.join(rows))
    print('"""')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python fetch_bda.py <id> [geotag_url]')
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'http://106.51.29.213/')
