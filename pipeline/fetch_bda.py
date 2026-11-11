"""Auto-fetch an auction's inputs so no row is transcribed by hand.

Two public sources, joined:
  1. A BDA geotag map (e.g. http://106.51.29.213/ or :9005) — its page embeds a GeoJSON FeatureCollection with,
     per plot, a serial no, site no, the two frontages, the area, and the polygon. BDA uses two field spellings
     (Sl_No/Site_No/East_to_We/North_to_S/Area/Division, and slNo/siteNo/eastWest/northSouth/areaSqm); both are read.
  2. KPPP public auction-search / view-auction — the base rate (Rs/sq m), bid dates, EMD/fee, notice number and the
     full title (which carries the layout). The geotag sometimes omits the layout, so it is taken from KPPP there.

Site numbers in the newer layouts (e.g. B5-SG-6247) are globally unique, so the join is exact; where a bare number
repeats across sub-blocks the locality group disambiguates it.

Output: auctions/<id>/geotag.json and a ready ROWS block + the AUCTION base facts, printed for notice.py.

Usage:
  python fetch_bda.py <id> <geotag_url> [default_group]
  python fetch_bda.py <id> auto [default_group]       # discover the geotag URL from bdakarnataka.in
"""
import json, os, re, subprocess, sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groups import group_of

HERE = os.path.dirname(os.path.abspath(__file__))
KAPI = 'https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service'
BDA_EAUCTION = 'https://www.bdakarnataka.in/api/pages/e-auction'
NL = chr(10)
norm = lambda s: re.sub(r'[^0-9A-Z]', '', str(s or '').upper())
# logical field -> candidate geotag property keys (prefix-matched, case-insensitive)
FIELD = dict(sl=['Sl_No', 'slNo'], site=['Site_No', 'siteNo'], ew=['East_to_We', 'eastWest', 'East'],
             ns=['North_to_S', 'northSouth', 'North'], area=['Area', 'areaSqm'], layout=['Layout', 'Village'], div=['Division'])


def getp(props, field):
    for cand in FIELD[field]:
        for k, v in props.items():
            if k.lower().startswith(cand.lower()):
                return v
    return None


def curl(url, *args):
    return subprocess.run(['curl', '-sSL', '-m', '90', *args, url], capture_output=True, text=True, encoding='utf8', errors='replace').stdout


def fetch_geotag(url):
    """Pull the inline GeoJSON FeatureCollection out of a BDA geotag map page."""
    html = curl(url)
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


def discover_geotag_url():
    """Find geotag map links on the bdakarnataka.in e-auction page (the BDA geotag servers / GIS viewers)."""
    raw = curl(BDA_EAUCTION, '-H', 'Accept: application/json')
    urls = re.findall(r'https?://(?:106\.51\.29\.213[:0-9]*|[a-z0-9.-]*drv\.tw)[^\s"<>)]*', raw)
    seen = []
    for u in urls:
        if u not in seen: seen.append(u)
    return seen


def kppp_search(status, word, page=0):
    r = subprocess.run(['curl', '-s', '-m', '40', '-D', '-', '-X', 'POST', f'{KAPI}/search/auction-search?page={page}&pageSize=10',
                        '-H', 'Content-Type: application/json', '-d', json.dumps({'auctionStatus': status, 'auctionTitle': word})],
                       capture_output=True, text=True, encoding='utf8')
    head, _, body = r.stdout.partition(NL + NL)
    total = next((int(l.split(':')[1]) for l in head.splitlines() if l.lower().startswith('x-total-count')), 0)
    try: return json.loads(body or '[]'), total
    except Exception: return [], total


def kppp_index(words, statuses):
    """norm(Site_No) -> newest lot {base, title, group, bidStart, eoi, emd, fee, no, id}."""
    lots = {}
    for st in statuses:
        for w in words:
            rows, total = kppp_search(st, w)
            pages = [rows] + list(ThreadPoolExecutor(6).map(lambda p: kppp_search(st, w, p)[0], range(1, (total + 9) // 10)))
            for rs in pages:
                for a in rs:
                    if a['auctionNoticeNumber'].startswith('BDA/'): lots[a['auctionNoticeId']] = a

    def detail(a):
        b = curl(f"{KAPI}/{a['auctionNoticeId']}/view-auction")
        try:
            d = json.loads(b); n = d['auctionNoticeDTO']; slot = (d.get('auctionBiddingSlotDTO') or [{}])[0]
            sch = ((d.get('auctionScheduleInformationDTO') or {}).get('auctionSchedule') or {})
            site = re.search(r'Site No-?\s*([0-9A-Za-z/-]+)', a['auctionTitle'])   # includes hyphens: B5-SG-6247
            a['_site'] = site.group(1) if site else ''
            a['_base'] = float(n.get('totalAmount') or 0); a['_start'] = slot.get('auctionStartDate'); a['_eoi'] = sch.get('auctionParticipationInterestDate')
            a['_emd'] = sch.get('fullEmd'); a['_fee'] = sch.get('auctionFee')
        except Exception:
            a['_base'] = None
        return a
    dkey = lambda s: tuple(int(x) for x in reversed((s or '01-01-1900 00:00:00').split()[0].split('-')))
    idx = {}
    for a in sorted(ThreadPoolExecutor(8).map(detail, lots.values()), key=lambda a: dkey(a.get('_start'))):
        if not a.get('_base'): continue
        layout = (a['auctionTitle'].split(' at ', 1) + [''])[1]
        idx[norm(a['_site'])] = dict(base=a['_base'], title=a['auctionTitle'], layout=layout, group=group_of(a['auctionTitle']),
                                     bidStart=a.get('_start'), eoi=a.get('_eoi'), emd=a.get('_emd'), fee=a.get('_fee'), no=a['auctionNoticeNumber'])
    return idx


def build(aid, geo_url, default_group=None):
    if geo_url == 'auto':
        cands = discover_geotag_url()
        print('discovered geotag URLs on bdakarnataka.in:'); [print('  ', u) for u in cands]
        geo_url = next((u for u in cands if '106.51.29.213' in u), cands[0] if cands else None)
        if not geo_url: raise SystemExit('could not discover a geotag URL — pass it explicitly')
        print('using:', geo_url)
    gj = fetch_geotag(geo_url)
    feats = gj['features']
    # KPPP keywords from whatever layouts/titles we can see (geotag layout, else broad BDA locality set)
    kw = sorted({w for f in feats for w in re.findall(r'[A-Za-z]{5,}', getp(f['properties'], 'layout') or '')})
    kw = [w for w in kw if w.upper() in ('BANASHANKARI', 'ANJANAPURA', 'ARKAVATHI', 'ARKAVATHY', 'VISHVESHWARAH', 'NAGAR', 'KEMPEGOWDA', 'NADAPRABHU')]
    if not kw: kw = ['KEMPEGOWDA', 'NADAPRABHU', 'BANASHANKARI', 'ANJANAPURA', 'ARKAVATHI']
    bases = kppp_index(kw, ['PUBLISHED', 'LIVE_AUCTION', 'BIDDING_CLOSED', 'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED', 'UNDER_EVALUATION', 'EVALUATED', 'FINALIZED'])
    rows, matched, facts = [], 0, Counter()
    for f in feats:
        p = f['properties']; site = str(getp(p, 'site') or '').strip()
        k = bases.get(norm(site))
        layout = (getp(p, 'layout') or (k['layout'] if k else '') or '').strip()
        group = group_of(layout) or (k['group'] if k else None) or default_group or '?'
        if k:
            matched += 1
            facts[('eoi', k['eoi'])] += 1; facts[('start', k['bidStart'])] += 1; facts[('emd', k['emd'])] += 1; facts[('fee', k['fee'])] += 1; facts[('baserate', int(k['base']))] += 1
        rows.append('|'.join([str(getp(p, 'sl') or ''), site, layout, str(getp(p, 'ew') or ''), str(getp(p, 'ns') or ''),
                              str(getp(p, 'area') or ''), str(int(k['base']) if k else ''), str(getp(p, 'div') or 'South'), group]))
    # Normalize geotag properties to the canonical keys analyze.py matches on ('Sl. No.', 'Site No.'),
    # since BDA's live feeds vary (Sl_No/slNo, Site_No/siteNo). Keep geometry and a few useful fields.
    for f in feats:
        p = f['properties']
        f['properties'] = {'Sl. No.': str(getp(p, 'sl') or '').strip(), 'Site No.': str(getp(p, 'site') or '').strip(),
                           'Layout': str(getp(p, 'layout') or '').strip(), 'Area': getp(p, 'area'),
                           'East to West': getp(p, 'ew'), 'North to South': getp(p, 'ns'),
                           'Division': getp(p, 'div'), 'Remarks': p.get('Remarks') or p.get('remarks') or ''}
    out = os.path.join(HERE, 'auctions', aid)
    os.makedirs(out, exist_ok=True)
    json.dump(gj, open(os.path.join(out, 'geotag.json'), 'w', encoding='utf8'), ensure_ascii=False)
    top = lambda key: (Counter({v: c for (t, v), c in facts.items() if t == key}).most_common(1) or [(None, 0)])[0][0]
    print(f'geotag: {len(feats)} sites -> auctions/{aid}/geotag.json   (source {geo_url})')
    print(f'KPPP base rates matched: {matched}/{len(feats)}  groups: {sorted(set(r.split("|")[-1] for r in rows))}')
    print(f'AUCTION facts (most common): base {top("baserate")} Rs/m2 | EOI {top("eoi")} | bidStart {top("start")} | EMD {top("emd")} | fee {top("fee")}')
    print('--- ROWS (paste into auctions/%s/notice.py) ---%sROWS = """%s%s%s"""' % (aid, NL, NL, NL.join(rows), NL))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('usage: python fetch_bda.py <id> <geotag_url|auto> [default_group]')
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
