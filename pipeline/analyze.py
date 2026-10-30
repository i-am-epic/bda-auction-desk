import json, math, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sites import ROWS, WITHDRAWN, MARKET, LOCALITY, METRO, HUBS

SQFT = 10.7639
geo = json.load(open(sys.argv[1]))
OUT = sys.argv[2]

def norm(s): return re.sub(r'[^0-9A-Z]', '', s.upper())

def dim(expr):
    """Average length (m) of a side expression like '[7.50+3.10]/2' or '(14.10+14.80)2'. None if composite."""
    e = expr.strip().replace('[', '(').replace(']', ')')
    if '(1)' in e or 'x' in e.lower(): return None
    e = re.sub(r'\)\s*2$', ')/2', e)
    if not re.fullmatch(r'[0-9.+*/() ]+', e): return None
    try: return float(eval(e, {'__builtins__': {}}))
    except Exception: return None

def sides(expr):
    """Individual side lengths in a trapezoid expression (to judge irregularity)."""
    e = expr.replace('[', '(').replace(']', ')')
    m = re.match(r'\(\s*([\d.]+)\s*\+\s*([\d.]+)\s*\)', e)
    return [float(m.group(1)), float(m.group(2))] if m else None

def hav(a, b, c, d):
    R = 6371.0; p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    return 2 * R * math.asin(math.sqrt(math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))

def poly_metrics(coords):
    pts = coords[:-1] if coords[0] == coords[-1] else coords
    lat0 = sum(p[1] for p in pts) / len(pts)
    kx, ky = 111320 * math.cos(math.radians(lat0)), 110540
    xy = [(p[0]*kx, p[1]*ky) for p in pts]
    a = 0
    for i in range(len(xy)):
        x1, y1 = xy[i]; x2, y2 = xy[(i+1) % len(xy)]
        a += x1*y2 - x2*y1
    sl = [math.dist(xy[i], xy[(i+1) % len(xy)]) for i in range(len(xy))]
    return abs(a)/2, min(sl), max(sl), (sum(p[1] for p in pts)/len(pts), sum(p[0] for p in pts)/len(pts))

# index geotag features by (sl, site)
gidx = {}
for f in geo['features']:
    p = f['properties']
    g = f['geometry']
    ring = g['coordinates'][0] if g['type'] == 'Polygon' else g['coordinates'][0][0]
    gidx.setdefault(p['Sl. No.'].strip(), []).append((p, ring))

sites = []
for line in ROWS.strip().splitlines():
    sl, site, layout, ew, ns, area, rate, zone, grp = [x.strip() for x in line.split('|')]
    area, rate = float(area), float(rate)
    s = dict(sl=sl, site=site, layout=layout, ew=ew, ns=ns, area=area, rate=rate, zone=zone, group=grp,
             source='Corrigendum (added)' if sl.startswith('C') else 'Main notice', flags=[], status='active')
    if sl in WITHDRAWN:
        s['status'] = 'withdrawn'
        s['flags'].append(('bad', 'Withdrawn by corrigendum (already allotted) — not on sale'))
    if sl == '77':
        s['flags'].append(('bad', 'Corrigendum changes area to 233.98 m², but printed dimensions (6.5 × 12.19 m) give 79.23 m² and the BDA map polygon measures ≈128 m² — ask BDA which area you will be billed for'))
        s['area_corr'] = 233.98

    # --- dimension check
    a, b = dim(ew), dim(ns)
    if sl == '11': a = 21.60/2  # '[1/2*21.60]' = triangle -> avg width 10.8
    if sl == '23': b = 3.5/2    # '(0.50*3.50)/2' printed; area 31.5 implies avg depth 1.75 m
    s['dimArea'] = round(a*b, 2) if a and b else None
    if s['dimArea'] and abs(s['dimArea'] - area) / area > 0.03:
        s['flags'].append(('warn', f'Printed area {area} m² does not match dimensions ({s["dimArea"]} m²)'))
    s['minW'] = round(min(a, b), 2) if a and b else None
    irr = 0
    for e in (ew, ns):
        sd = sides(e)
        if sd: irr = max(irr, abs(sd[0]-sd[1]) / max(sd))
    if sl in ('11', '23', '105', '134'): irr = max(irr, 0.6)
    s['irregularity'] = round(irr, 2)
    narrowest = min([x for x in sum([sides(e) or [] for e in (ew, ns)], []) + [v for v in (a, b) if v]] or [99])
    s['narrowest'] = narrowest
    if s['status'] == 'active':
        if narrowest < 3: s['flags'].append(('bad', f'A side is only {narrowest} m — wedge/strip, hard to build on'))
        if area < 40: s['flags'].append(('bad', f'Very small ({area} m² ≈ {area*SQFT:.0f} sq ft) — likely a leftover strip; check buildability before bidding'))
        elif area < 60: s['flags'].append(('warn', f'Small plot ({area*SQFT:.0f} sq ft) — limited to a compact G+2 house'))
        if irr >= 0.5: s['flags'].append(('warn', 'Highly irregular shape (sides differ by 50%+) — loses usable area to setbacks'))
        elif irr >= 0.25: s['flags'].append(('info', 'Moderately irregular (trapezoid) shape'))

    # --- geotag
    cand = gidx.get(sl, []) if not sl.startswith('C') else []
    match = [c for c in cand if norm(c[0]['Site No.']) == norm(site)] or cand
    if match:
        p, ring = match[0]
        pa, smin, smax, (clat, clon) = poly_metrics(ring)
        s.update(lat=clat, lon=clon, geotag='official', polygon=[[pt[1], pt[0]] for pt in ring], polyArea=round(pa, 1))
        if norm(p['Site No.']) != norm(site):
            s['flags'].append(('warn', f'Geotag map labels this site "{p["Site No."]}" but notice says "{site}"'))
        if (p.get('Remarks') or '').strip():
            s['flags'].append(('bad' if s['status'] == 'active' else 'info', f'BDA geotag remark: "{p["Remarks"].strip()}" — physical site not located by BDA survey'))
        if len(cand) > 1:
            s['flags'].append(('info', 'Geotag map has duplicate polygons for this serial number'))
        dev = (pa - area) / area
        s['polyDev'] = round(dev*100, 1)
        if abs(dev) > 0.4 and s['status'] == 'active' and s['sl'] != '77':
            s['flags'].append(('warn' if abs(dev) > 1 else 'info', f'BDA map polygon measures ≈ {pa:.0f} m² vs notified {area} m² ({dev*100:+.0f}%) — the map is hand-drawn, but measure on the ground'))
    else:
        same = [x for x in sites if x['layout'] == layout and x.get('geotag') == 'official']
        if same:
            s.update(lat=sum(x['lat'] for x in same)/len(same), lon=sum(x['lon'] for x in same)/len(same),
                     geotag='approx', geoNote=f'Approximate: centre of {len(same)} officially geotagged site(s) in the same block')
        elif layout in LOCALITY:
            la, lo, note = LOCALITY[layout]
            s.update(lat=la, lon=lo, geotag='approx', geoNote='Approximate: ' + note)
        else:
            sib = [x for x in sites if x['group'] == grp and x.get('geotag') == 'official' and layout.split(',')[-1].strip() in x['layout']]
            sib = sib or [x for x in sites if x['group'] == grp and x.get('geotag') == 'official']
            s.update(lat=sum(x['lat'] for x in sib)/len(sib), lon=sum(x['lon'] for x in sib)/len(sib),
                     geotag='approx', geoNote=f'Approximate: centre of nearby geotagged sites in {MARKET[grp]["name"]}')
        if s['status'] == 'active':
            s['flags'].append(('warn', 'Not on BDA geotag map — location here is our approximation; get exact spot from BDA engineer before bidding'))
    sites.append(s)

# fix the approx ones for the corrigendum 4th H block (sl 57 is a 'Not found' polygon; use FE BSK 4th T cluster instead)
for s in sites:
    if s['sl'] == 'C1':
        cl = [x for x in sites if "4th 'T' Block" in x['layout'] and x.get('geotag') == 'official']
        s['lat'] = sum(x['lat'] for x in cl)/len(cl); s['lon'] = sum(x['lon'] for x in cl)/len(cl)
        s['geoNote'] = "Approximate: 4th 'H' Block sits beside the 4th 'T' Block cluster (BDA's only 4th 'H' polygon is marked 'Not found')"

# --- pricing & scoring
TIER_RENT = {2: 17, 3: 21, 4: 27, 5: 33}       # Rs per sq ft built-up per month (gross, new G+3 rental)
BUILD_COST = 2600                                # Rs per sq ft, standard spec construction
STAMP = 0.066                                     # ~5.6% stamp duty incl. cess/surcharge + 1% registration (Karnataka)

for s in sites:
    m = MARKET[s['group']]; area = s['area']
    billed = s.get('area_corr', area)
    s['locality'] = m['name']; s['locNote'] = m['story']; s['tier'] = m['tier']
    s['areaSqft'] = round(area*SQFT)
    s['ratePerSqft'] = round(s['rate']/SQFT)
    s['baseTotal'] = round(billed*s['rate'])
    s['minBidRate'] = round(s['rate']*1.10)
    s['minBidTotal'] = round(billed*s['rate']*1.10)
    # usability factor
    f = 1.0
    if area < 35: f *= 0.62
    elif area < 50: f *= 0.78
    elif area < 70: f *= 0.9
    elif area < 100: f *= 0.96
    if s['narrowest'] < 3: f *= 0.8
    if s['irregularity'] >= 0.5: f *= 0.88
    elif s['irregularity'] >= 0.25: f *= 0.95
    s['usability'] = round(f, 2)
    fair_lo, fair_mid, fair_hi = [m[k]*SQFT*f for k in ('lo', 'mid', 'hi')]
    s['fairRate'] = round(fair_mid); s['fairLo'] = round(fair_lo); s['fairHi'] = round(fair_hi)
    s['fairSqft'] = round(fair_mid/SQFT)
    s['fairTotal'] = round(fair_mid*area)
    s['marketSqft'] = [m['lo'], m['mid'], m['hi']]
    # BDA auctions usually clear somewhat below resale (buyers price in delay, as-is condition & no negotiation)
    exp = max(s['minBidRate']*1.03, fair_mid*0.90)
    s['expRate'] = round(exp); s['expTotal'] = round(exp*billed)
    s['maxBidRate'] = round(max(fair_mid*0.95, s['minBidRate']))
    s['maxBidTotal'] = round(s['maxBidRate']*billed)
    s['upside'] = round((fair_mid - s['minBidRate'])/s['minBidRate']*100, 1)
    s['premiumOverBase'] = round((fair_mid - s['rate'])/s['rate']*100, 1)
    # build potential (Bengaluru RMP-2015 zoning regs, conservative: FAR 1.75, road < 12 m assumed)
    far = 1.75
    s['builtUpSqft'] = round(area*SQFT*far)
    s['floors'] = 'G+1' if area < 40 else 'G+2' if area < 110 else 'G+3'
    s['use'] = ('Tiny home / kiosk — check plan sanction first' if area < 40 else
                'Compact independent house (1-2 BHK)' if area < 75 else
                'Independent house or 2-unit rental' if area < 140 else
                'G+3 rental: ~3-4 units (2BHK)' if area < 250 else
                'G+3 rental: 4-6 units, or a premium villa')
    s['buildCost'] = round(s['builtUpSqft']*BUILD_COST)
    s['stampReg'] = round(s['expTotal']*STAMP)
    s['tds'] = round(s['expTotal']*0.01) if s['expTotal'] > 5_000_000 else 0
    s['allIn'] = s['expTotal'] + s['stampReg'] + 50_000
    s['projectCost'] = s['allIn'] + s['buildCost']
    s['rentMonthly'] = round(s['builtUpSqft']*0.85*TIER_RENT[m['tier']])
    s['grossYield'] = round(s['rentMonthly']*12/s['projectCost']*100, 2)
    # nearest metro & hubs
    dm = sorted(((hav(s['lat'], s['lon'], la, lo), n) for n, la, lo in METRO))[0]
    s['metro'] = dict(name=dm[1], km=round(dm[0], 1))
    s['hubs'] = [dict(name=n, km=round(hav(s['lat'], s['lon'], la, lo), 1)) for n, la, lo in HUBS]
    s['hubs'].sort(key=lambda h: h['km'])
    s['hubs'] = s['hubs'][:3]

    # score
    if s['status'] == 'withdrawn':
        s['score'] = None; s['verdict'] = 'Withdrawn'
    else:
        value = max(0, min(10, s['upside']/4.5))                 # 45%+ upside = 10
        loc = {2: 4.5, 3: 6.5, 4: 8, 5: 9.5}[m['tier']]
        if s['metro']['km'] < 1.5: loc += 0.5
        elif s['metro']['km'] > 5: loc -= 0.7
        use = max(0, min(10, s['usability']*10 - (1.5 if area < 60 else 0) + (0.5 if area >= 150 else 0)))
        conf = 10
        for sev, _ in s['flags']:
            conf -= {'bad': 4, 'warn': 1.8, 'info': 0.4}[sev]
        conf = max(0, conf)
        sc = 0.40*value + 0.25*loc + 0.20*use + 0.15*conf
        if any(sev == 'bad' for sev, _ in s['flags']): sc = min(sc, 5.0)
        s['score'] = round(max(0, min(10, sc)), 1)
        s['scoreParts'] = dict(value=round(value, 1), location=round(loc, 1), usability=round(use, 1), confidence=round(conf, 1))
        s['verdict'] = ('Strong buy' if s['score'] >= 7.5 else 'Good' if s['score'] >= 6.3 else
                        'Fair / selective' if s['score'] >= 5 else 'Skip / high risk')
    # pros & cons
    pros, cons = [], []
    if s['upside'] >= 25: pros.append(f"Minimum bid (₹{s['minBidRate']/SQFT:,.0f}/sq ft) is ~{s['upside']:.0f}% below our resale estimate (₹{s['fairSqft']:,}/sq ft)")
    elif s['upside'] >= 8: pros.append(f"Modest headroom: ~{s['upside']:.0f}% between minimum bid and resale estimate")
    else: cons.append(f"Thin margin: minimum bid is only ~{s['upside']:.0f}% under our resale estimate — little room once bidding starts")
    if m['tier'] >= 4: pros.append('Established / high-demand locality with strong resale & rental depth')
    if m['tier'] <= 2: cons.append('Peripheral extension — civic works & occupancy still building up; slower resale')
    if s['metro']['km'] <= 2.5: pros.append(f"Metro within {s['metro']['km']} km ({s['metro']['name']})")
    elif s['metro']['km'] > 5: cons.append(f"Nearest metro ~{s['metro']['km']} km ({s['metro']['name']})")
    if 100 <= area <= 260 and s['irregularity'] < 0.25: pros.append('Practical size & regular shape — easy to plan a G+3 rental or family home')
    if area > 300: pros.append(f"Large plot ({s['areaSqft']:,} sq ft) — villa or 4-6 unit rental potential")
    if area > 300: cons.append(f"High ticket: expected winning bid ≈ ₹{s['expTotal']/1e7:.2f} Cr")
    pros.append('BDA allotment = clean title & BDA khata; loans readily available from major banks') if s['status'] == 'active' else None
    if s['group'].startswith('ARK'): cons.append('Arkavathy layout has a history of land-loser litigation & denotification disputes — get the specific survey no. checked')
    cons.append('Sold "as is": road width, encroachment, drains & level must be checked on site (BDA T&C #27)')
    for sev, t in s['flags']:
        if sev in ('bad', 'warn') and t not in cons: cons.append(t)
    s['pros'], s['cons'] = pros, cons
    s['flags'] = [dict(sev=a, text=b) for a, b in s['flags']]

json.dump(sites, open(OUT, 'w', encoding='utf8'), ensure_ascii=False)
act = [s for s in sites if s['status'] == 'active']
print('total', len(sites), 'active', len(act), 'approx-geo', sum(1 for s in act if s['geotag'] == 'approx'))
for s in sorted(act, key=lambda s: -s['score'])[:12]:
    print(s['sl'], s['site'], s['locality'][:30], s['area'], s['score'], s['verdict'], s['upside'], s.get('polyDev'))
print('---- worst')
for s in sorted(act, key=lambda s: s['score'])[:15]:
    print(s['sl'], s['site'], s['area'], s['score'], [f['text'][:50] for f in s['flags']])
print('---- polygon deviations')
for s in act:
    if s.get('polyDev') is not None and abs(s['polyDev']) > 20: print(s['sl'], s['site'], s['area'], s['polyArea'], s['polyDev'])
