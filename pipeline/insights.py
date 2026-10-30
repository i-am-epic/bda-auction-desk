"""Second-pass analysis: auction history (KPPP), terrain/surroundings (OSM + SRTM), drawn polygons for untagged sites,
competition and win odds, great finds, specific descriptions, vastu and buyer personas.
Usage: python insights.py build/data.json build/geo_extra.json build/kppp_history.json build/kppp_live.json build/data2.json"""
import json, math, re, sys, os, statistics
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from market import MARKET
from projects import PROJECTS

SQFT = 10.7639
sites = json.load(open(sys.argv[1], encoding='utf8'))
geo = json.load(open(sys.argv[2], encoding='utf8'))
hist = json.load(open(sys.argv[3], encoding='utf8'))
live = json.load(open(sys.argv[4], encoding='utf8'))
OUT = sys.argv[5]
ROADS = json.load(open(sys.argv[6], encoding='utf8')) if len(sys.argv) > 6 else {}
MODELS = json.load(open(sys.argv[7], encoding='utf8')) if len(sys.argv) > 7 else None   # models.py: learned sell odds + winning price
PHI = lambda z: 0.5*(1 + math.erf(z/math.sqrt(2)))
_BR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inputs', 'bid_results.json')
FINALS = {(b['group'], re.sub(r'[^0-9A-Z]', '', str(b['site']).upper())): b for b in (json.load(open(_BR, encoding='utf8')) if os.path.exists(_BR) else []) if b['group']}
key = lambda s: s['sl'] + '|' + s['site']
norm = lambda t: re.sub(r'[^0-9A-Z]', '', str(t).upper())

from groups import group_of, site_of  # noqa: E402

def ymd(d):  # 'dd-mm-yyyy hh:mm:ss' -> (yyyy, mm)
    return (int(d[6:10]), int(d[3:5])) if d else None

SOLD, UNSOLD = {'FINALIZED', 'BIDDING_CLOSED'}, {'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED'}
G = defaultdict(lambda: dict(sold=0, unsold=0, rates=defaultdict(list)))
past = defaultdict(list)
legal_block = defaultdict(list)   # (group, block title) -> lots BDA pulled for court cases / forest or lake buffers
for h in hist:
    g = group_of(h['auctionTitle'])
    if not g: continue
    when = ymd(h.get('bidDate'))
    if not when or when >= (2026, 11): continue          # skip the current (T-15) round
    if h['statusKey'] in SOLD: G[g]['sold'] += 1
    elif h['statusKey'] in UNSOLD: G[g]['unsold'] += 1
    if h.get('baseRate'): G[g]['rates'][when[0] + (when[1] - 1)/12].append(h['baseRate'])
    past[(g, site_of(h['auctionTitle']))].append(dict(date=h['bidDate'][:10], status=h['statusKey'], base=h.get('baseRate'), no=h['auctionNoticeNumber'], reason=h.get('recallReason'),
        final=(FINALS.get((g, site_of(h['auctionTitle']))) or {}).get('final') if h['statusKey'] in SOLD else None))
    if h.get('recallReason') and re.search(r'forest|buffer|lake|court|litig', h['recallReason'], re.I):
        block = re.sub(r'^.*? AT ', '', h['auctionTitle'].upper()).strip()
        legal_block[(g, re.sub(r'[^A-Z0-9 ]', '', block))].append(dict(site=site_of(h['auctionTitle']), reason=h['recallReason'].strip(), date=h['bidDate'][:10]))

hist_summary = {}
for g, v in G.items():
    tot = v['sold'] + v['unsold']
    pts = sorted((t, statistics.median(r)) for t, r in v['rates'].items())
    yearly = defaultdict(list)
    for t, r in pts: yearly[int(t)].append(r)
    series = [(y, round(statistics.median(r))) for y, r in sorted(yearly.items())]
    cagr = None
    if len(pts) >= 2 and pts[-1][0] - pts[0][0] >= 0.9:
        cagr = round(((pts[-1][1]/pts[0][1]) ** (1/(pts[-1][0]-pts[0][0])) - 1)*100, 1)
    hist_summary[g] = dict(lots=tot, sold=v['sold'], unsold=v['unsold'], sellThrough=round(v['sold']/tot*100) if tot else None,
                           baseSeries=series, baseCagr=cagr)

# ---------- KPPP lot for each current site ----------
lots = defaultdict(list)
for a in live:
    lots[(group_of(a['auctionTitle']), site_of(a['auctionTitle']))].append(a)

# ---------- helpers ----------
def tolatlon(lat0, lon0, pts):
    return [[lat0 + y/110540, lon0 + x/(111320*math.cos(math.radians(lat0)))] for x, y in pts]

def side_pair(expr):
    e = expr.replace('[', '(').replace(']', ')')
    m = re.match(r'\(\s*([\d.]+)\s*\+\s*([\d.]+)\s*\)', e)
    return (float(m.group(1)), float(m.group(2))) if m else None

def avg(expr):
    e = expr.replace('[', '(').replace(']', ')').strip()
    e = re.sub(r'\)\s*2$', ')/2', e)
    try: return float(eval(e, {'__builtins__': {}})) if re.fullmatch(r'[0-9.+*/() ]+', e) else None
    except Exception: return None

def draw(s):
    a, b = avg(s['ew']), avg(s['ns'])
    if not (a and b):
        a = b = math.sqrt(s['area'])
    ew, ns = side_pair(s['ew']), side_pair(s['ns'])
    if ew:   # north edge = first figure, south edge = second
        p, q = ew; pts = [(-p/2, b/2), (p/2, b/2), (q/2, -b/2), (-q/2, -b/2)]
    elif ns: # west edge = first, east edge = second
        p, q = ns; pts = [(-a/2, -p/2), (-a/2, p/2), (a/2, q/2), (a/2, -q/2)]
    else:
        pts = [(-a/2, -b/2), (-a/2, b/2), (a/2, b/2), (a/2, -b/2)]
    return pts, max(a, b)

def feet(m): return round(m*3.2808)

STD = [(20, 30), (30, 40), (30, 50), (40, 60), (50, 80), (60, 90)]
def size_label(s):
    a, b = avg(s['ew']), avg(s['ns'])
    if not (a and b): return f"irregular, about {s['areaSqft']:,} ft²"
    fa, fb = sorted((feet(a), feet(b)))
    near = min(STD, key=lambda d: abs(d[0]*d[1] - fa*fb) + 4*abs(d[0]-fa))
    std = f"close to a standard {near[0]}x{near[1]}" if abs(near[0]*near[1] - fa*fb) / (near[0]*near[1]) < 0.12 else 'a non-standard size'
    return f"about {fa} x {fb} ft ({std})"

KIND = dict(lake='lake / tank', drain='stormwater drain or stream', canal='canal / river', htline='high-tension power line',
            ltline='overhead power line', majorroad='main road (arterial)', midroad='busy collector road', rail='railway line',
            cemetery='burial ground', garbage='garbage / waste site', stp='sewage treatment plant', industrial='industrial area',
            quarry='quarry', green='park / forest', school='school / college', hospital='hospital / clinic', shop='supermarket / store',
            bus='bus stop', road='road')
nm = lambda v: f" ({v['name']})" if v.get('name') else ''

# ---------- per-site pass ----------
approx_slot = defaultdict(int)
for s in sites:
    m = MARKET[s['group']]
    g = geo.get(key(s), {})
    near = g.get('near', {})
    s['geo'] = g
    hs = hist_summary.get(s['group'], {})
    s['history'] = hs

    # polygon for sites BDA has not mapped
    if not s.get('polygon'):
        pts, span = draw(s)
        i = approx_slot[(round(s['lat'], 3), round(s['lon'], 3))]; approx_slot[(round(s['lat'], 3), round(s['lon'], 3))] += 1
        off = (i - 0) * (span + 8)
        s['polygon'] = tolatlon(s['lat'], s['lon'] + off/(111320*math.cos(math.radians(s['lat']))), pts)
        s['lon'] += off/(111320*math.cos(math.radians(s['lat'])))
        s['polyDrawn'] = True

    # KPPP lot
    cand = lots.get((s['group'], norm(s['site'])), [])
    if len(cand) > 1: cand = sorted(cand, key=lambda a: -a['auctionNoticeId'])
    s['kppp'] = dict(no=cand[0]['auctionNoticeNumber'], id=cand[0]['auctionNoticeId'], title=cand[0]['auctionTitle']) if cand else None

    # past appearances of this exact site
    prev = sorted(past.get((s['group'], norm(s['site'])), []), key=lambda p: p['date'][6:] + p['date'][3:5])
    s['prevRounds'] = prev
    unsold_before = sum(1 for p in prev if p['status'] in UNSOLD)
    for p in prev:
        if p.get('reason') and re.search(r'court|litig', p['reason'], re.I):
            s['flags'].append(dict(sev='bad', text=f"BDA pulled this exact site from auction {p['no']} ({p['date']}) citing \"{p['reason']}\". Get written confirmation the case is closed before bidding"))
        elif p.get('reason') and re.search(r'forest|buffer|lake', p['reason'], re.I):
            s['flags'].append(dict(sev='bad', text=f"BDA pulled this exact site earlier ({p['date']}) citing \"{p['reason']}\""))
    blk = re.sub(r'[^A-Z0-9 ]', '', s['layout'].upper().replace(',', ''))
    for (gk, bk), hits in legal_block.items():
        if gk != s['group']: continue
        words = set(bk.split()) - {'SITE', 'NO', 'AT', 'OF', 'THE', 'LAYOUT', 'STAGE', 'BLOCK'}
        if words and words <= set(blk.split()) | {'F', 'E', 'FE', 'FURTHER', 'EXTENSION'}:
            for hgt in hits:
                if hgt['site'] != norm(s['site']) and re.search(r'forest|buffer|lake', hgt['reason'], re.I):
                    s['flags'].append(dict(sev='warn', text=f"Neighbouring Site {hgt['site']} in this block was withdrawn ({hgt['date']}) for \"{hgt['reason']}\". Check this plot is outside that buffer"))

    # ---------- risks & positives from surroundings ----------
    risks, goods = [], []
    def d(k): return near.get(k, {}).get('m', 99999)
    if d('lake') < 75: risks.append(('bad', f"Lake/tank edge only {d('lake')} m away{nm(near['lake'])}. Lake buffer rules can restrict building, and low ground here can flood"))
    elif d('lake') < 400: goods.append(f"Lake{nm(near['lake'])} {d('lake')} m away: open views and cooler air, but check the plot is above lake level")
    if d('drain') < 35: risks.append(('bad', f"Stormwater drain/stream within {d('drain')} m{nm(near['drain'])}. Rajakaluve buffer (15-50 m by drain class) may block sanction, and it can smell and flood"))
    elif d('drain') < 100: risks.append(('warn', f"Stormwater drain/stream {d('drain')} m away{nm(near['drain'])}. Watch for flooding and mosquitoes in the monsoon"))
    if d('canal') < 60: risks.append(('warn', f"Canal/river {d('canal')} m away{nm(near['canal'])}"))
    if d('htline') < 30: risks.append(('bad', f"High-tension line {d('htline')} m away. KPTCL clearance corridors restrict building, and banks may hesitate"))
    elif d('htline') < 100: risks.append(('warn', f"High-tension power line {d('htline')} m away (visible, possible hum)"))
    if d('majorroad') < 60: risks.append(('warn', f"Arterial road {d('majorroad')} m away{nm(near['majorroad'])}: noise and dust, but commercial potential"))
    elif d('midroad') < 40: risks.append(('info', f"On or next to a collector road{nm(near['midroad'])}: more traffic, better visibility"))
    if d('rail') < 200: risks.append(('warn', f"Railway line {d('rail')} m away: train noise"))
    if d('cemetery') < 200: risks.append(('warn', f"Burial ground {d('cemetery')} m away. Many local buyers avoid this, which hurts resale"))
    if d('stp') < 500: risks.append(('warn', f"Sewage treatment plant {d('stp')} m away: possible odour"))
    if d('garbage') < 600: risks.append(('warn', f"Garbage/waste site {d('garbage')} m away"))
    if d('industrial') < 250: risks.append(('info', f"Industrial land {d('industrial')} m away"))
    if d('quarry') < 1000: risks.append(('warn', f"Quarry {d('quarry')} m away: blasting dust and vibration"))
    if d('green') < 300: goods.append(f"Park/greenery{nm(near['green'])} {d('green')} m away")
    if d('school') < 1000: goods.append(f"School{nm(near['school'])} {d('school')} m away")
    if d('hospital') < 2000: goods.append(f"Hospital/clinic{nm(near['hospital'])} {d('hospital')/1000:.1f} km away")
    if d('shop') < 1000: goods.append(f"Daily shopping{nm(near['shop'])} {d('shop')} m away")
    if d('bus') < 600: goods.append(f"Bus stop {d('bus')} m away")
    elif d('bus') > 1500 and near: risks.append(('info', 'No bus stop mapped within 1.5 km* (OSM may be incomplete)'))
    # ---------- road width (current: OSM or estimate; planned: BBMP/RMP map) ----------
    rd = dict(ROADS.get(key(s), {}))
    pl = rd.get('planned')
    if pl and pl['width'] <= 30 and rd.get('conf') == 'Estimated*':
        rd.update(width=pl['width'], source=f"RMP planned width of the road beside it ({pl['width']:.0f} m); built width may be narrower*", conf='Estimated*')
        rd.pop('range', None)
        rd['ft'] = round(pl['width']*3.28); rd['far'] = 1.75 if pl['width'] < 12 else 2.25 if pl['width'] < 18 else 2.5
    if pl and pl['width'] >= 45 and pl['inside']:
        risks.append(('warn', f"The RMP road-width map shows a planned {pl['width']:.0f} m road (likely the Peripheral Ring Road) whose corridor reaches this plot ({pl['dist']} m from its centreline). The map is coarse*; get written confirmation from BDA that the site is outside the PRR alignment"))
    elif pl and pl['width'] >= 45:
        goods.append(f"Planned {pl['width']:.0f} m arterial (likely the PRR) about {pl['dist']} m away: future connectivity, plus noise once built")
    s['road'] = rd
    # ---------- commercial track: small or odd plots on wide roads can work as shops/offices ----------
    s['commercial'] = None
    on_wide = 18 <= (rd.get('width') or 0) < 45 or (pl and 18 <= pl['width'] < 45 and pl['dist'] <= pl['width']/2 + 12)               or d('majorroad') < 35 or d('midroad') < 25
    if on_wide and s['status'] == 'active':
        A, B = avg(s['ew']), avg(s['ns'])
        L, D = (max(A, B), min(A, B)) if A and B else (math.sqrt(s['area']),)*2
        wedge = s['irregularity'] >= 0.5 or s['narrowest'] < 1.5
        dmax = max([x for x in sum([list(side_pair(e) or []) for e in (s['ew'], s['ns'])], []) + [D] if x < L] or [D])
        MIN_D = 1.8   # shallowest shop worth renting, after the front setback
        if wedge:   # tapering strip, treated as a triangle; 0.75 m front + 0.6 m side setback (plots <= 60 m2, GBA 2026*)
            dmax = max(dmax, 2*s['area']/L)
            run = L * max(0, 1 - (MIN_D + 0.75)/dmax) - 0.6
            usable = max(0, run) * ((dmax - 0.75) + MIN_D)/2
        else:
            usable = (max(0, (L - 0.6) * (D - 0.75)) if D - 0.75 >= MIN_D else 0) if s['area'] <= 60 else s['area'] * 0.62
        gf = usable * SQFT
        upper = min(gf * (1 if D >= 3.5 and not wedge else 0.8) * (2 if s['area'] >= 60 else 1), max(0, s['area']*SQFT*rd.get('far', 1.75) - gf))
        rate = {2: 35, 3: 45, 4: 60, 5: 80}[m['tier']]
        rent = round(gf*rate + upper*rate*0.4)
        build = round((gf + upper)*2800)
        income_value = max(0, (rent*12/0.065 - build) * 0.75)   # 6.5% gross yield*, minus 25% for commercial-permission risk
        s['commercial'] = dict(usableM2=round(usable, 1), gfSqft=round(gf), upperSqft=round(upper), rent=rent, build=build,
            incomeValue=round(income_value), rate=rate, wedge=wedge, frontage=round(L, 1), depth=round(dmax if wedge else D, 2),
            road=(f"planned {pl['width']:.0f} m (~{pl['width']*3.28:.0f} ft) road on the RMP map" if pl and pl['width'] >= 18 else
                  f"{rd.get('width')} m road" if (rd.get('width') or 0) >= 18 else 'a main / collector road'))
        if gf >= 85:   # a usable kiosk or shop exists: size and shape problems become 'check', not 'risk'
            for fx in s['flags']:
                if fx['sev'] == 'bad' and (fx['text'].startswith('A side is only') or fx['text'].startswith('Very small')):
                    fx['sev'] = 'warn'; fx['text'] += ' (as a house; workable as a shop on this road*)'
    s['surroundRisks'] = [dict(sev=a, text=b) for a, b in risks]
    s['surroundGoods'] = goods

    # ---------- terrain & vastu ----------
    facing = g.get('facing'); aspect = g.get('aspect')
    vastu = []
    if facing in ('East', 'North', 'North-East'): vastu.append(('good', f"{facing}-facing (road on the {facing.lower()} side), which most buyers prefer"))
    elif facing in ('South', 'West', 'South-West'): vastu.append(('bad', f"{facing}-facing. Many vastu-minded buyers avoid this; expect 3-8% lower resale"))
    elif facing: vastu.append(('neutral', f"{facing}-facing"))
    if aspect in ('North', 'East', 'North-East'): vastu.append(('good', f"Ground slopes down towards the {aspect.lower()}, which vastu favours"))
    elif aspect in ('South', 'West', 'South-West'): vastu.append(('bad', f"Ground slopes down towards the {aspect.lower()}, which vastu does not favour; can be fixed with filling"))
    elif aspect == 'Flat': vastu.append(('neutral', 'Ground is practically flat'))
    s['vastu'] = [dict(kind=a, text=b) for a, b in vastu]
    vastu_adj = (0.03 if facing in ('East', 'North', 'North-East') else -0.04 if facing in ('South', 'West', 'South-West') else 0)
    rw = s['road'].get('width') or 9
    vastu_adj += 0.06 if rw >= 18 else 0.03 if rw >= 12 else -0.05 if rw < 7.5 else 0
    # build potential with the road-width FAR
    far = s['road'].get('far', 1.75)
    s['far'] = far
    s['builtUpSqft'] = round(s['area']*SQFT*far)
    s['floors'] = 'G+1' if s['area'] < 40 else 'G+2' if s['area'] < 110 else 'G+3'
    s['buildCost'] = round(s['builtUpSqft']*2600)
    s['rentMonthly'] = round(s['builtUpSqft']*0.85*{2: 17, 3: 21, 4: 27, 5: 33}[m['tier']])
    # flags caused only by missing data are notes, not penalties
    for fx in s['flags']:
        if fx['text'].startswith('Not on BDA geotag map'): fx['sev'] = 'info'

    # ---------- pricing (refreshed market) ----------
    billed = s.get('area_corr', s['area'])
    f = s['usability']
    fair_mid = m['mid']*SQFT*f*(1+vastu_adj); fair_lo = m['lo']*SQFT*f*(1+vastu_adj); fair_hi = m['hi']*SQFT*f*(1+vastu_adj)
    # blend in real auction results: what winners actually paid per ft2 in this locality (weight grows with the number of results)
    s['comps'] = (MODELS or {}).get('comps', {}).get(s['group'])
    if s['comps']:
        w = s['comps']['n'] / (s['comps']['n'] + 8)
        k = ((1 - w)*m['mid'] + w*s['comps']['medianSqft']) / m['mid']
        fair_mid, fair_lo, fair_hi = fair_mid*k, fair_lo*k, fair_hi*k
    s['valueBasis'] = 'residential'
    cm = s.get('commercial')
    if cm and cm['gfSqft'] >= 85 and (s['area'] < 120 or f < 0.9):
        inc = cm['incomeValue'] / s['area']
        if inc > fair_mid:
            fair_mid, fair_lo, fair_hi = inc, inc*0.8, inc*1.2
            s['valueBasis'] = 'commercial income*'
    # market-tested ceiling: if nobody bid at an earlier base, buyers valued this plot below 1.1x that base (grown since)
    s['marketCap'] = None
    for p in prev:
        if p['status'] in UNSOLD and p.get('base'):
            yrs = max(0, (2026 + 10/12) - (int(p['date'][6:10]) + (int(p['date'][3:5]) - 1)/12))
            cap_rate = 1.1*p['base']*(1 + m['cagr']/100)**yrs
            if s['marketCap'] is None or cap_rate < s['marketCap']['rate']:
                s['marketCap'] = dict(rate=round(cap_rate), base=p['base'], date=p['date'])
    if s['marketCap']:
        c = s['marketCap']['rate']
        s['marketCap']['applied'] = c < fair_mid
        fair_mid, fair_lo, fair_hi = min(fair_mid, c), min(fair_lo, c*0.9), min(fair_hi, c*1.08)
    last = prev[-1] if prev else None
    s['prevBase'] = last['base'] if last and last.get('base') else None
    s['baseChange'] = round((s['rate']/s['prevBase'] - 1)*100) if s['prevBase'] else None
    relisted_after_close = bool(last and last['status'] in SOLD)
    s['marketSqft'] = [m['lo'], m['mid'], m['hi']]
    s['fairRate'], s['fairLo'], s['fairHi'] = round(fair_mid), round(fair_lo), round(fair_hi)
    s['fairSqft'] = round(fair_mid/SQFT); s['fairTotal'] = round(fair_mid*s['area'])
    s['upside'] = round((fair_mid - s['minBidRate'])/s['minBidRate']*100, 1)
    s['premiumOverBase'] = round((fair_mid - s['rate'])/s['rate']*100, 1)

    # ---------- competition & expected bid ----------
    comp = m['demand']
    st = hs.get('sellThrough')
    if st is not None: comp += (st - 75)/20                     # layouts that often go unsold draw fewer bidders
    est_ticket = s['minBidTotal']
    if est_ticket < 50e5: comp += 0.6
    elif est_ticket > 3e7: comp -= 0.8
    elif est_ticket > 2e7: comp -= 0.4
    if f < 0.8: comp -= 0.8
    if unsold_before: comp -= 1.2
    if relisted_after_close: comp -= 0.8          # closed last time but came back: single bidder or a winner who did not pay
    if s['baseChange'] is not None and s['baseChange'] <= -10: comp += 0.8   # price cut attracts fresh interest
    if s['upside'] > 30: comp += 0.6
    if any(x['sev'] == 'bad' for x in s['flags']): comp -= 0.5
    comp = max(0.3, min(5, comp))
    s['competition'] = round(comp, 1)
    s['compLabel'] = 'Very high' if comp >= 4.3 else 'High' if comp >= 3.4 else 'Moderate' if comp >= 2.4 else 'Low' if comp >= 1.4 else 'Very low'
    # Expected winning bid, calibrated to BDA's Dec 2021 results: 296 sites sold for ~Rs 348 cr vs ~Rs 215 cr base (+62%),
    # corner sites +44% (thebengalurulive.com, 31 Dec 2021). Premium over base rises with competition; capped at the top of resale.
    def bid_at(c):
        prem = 0.10 + 0.55*(max(0.3, min(5, c))/5)**1.1
        return min(max(s['rate']*(1 + prem), s['minBidRate']*1.01), max(fair_hi, s['minBidRate']*1.01))
    exp = bid_at(comp)
    s['expRate'] = round(exp); s['expTotal'] = round(exp*billed)
    s['expLo'] = round(bid_at(comp - 0.8)*billed); s['expHi'] = round(bid_at(comp + 0.8)*billed)
    s['maxBidRate'] = round(max(fair_mid*0.95, s['minBidRate']*1.005)); s['maxBidTotal'] = round(s['maxBidRate']*billed)
    ml = (MODELS or {}).get('sites', {}).get(key(s))
    s['pSell'] = None
    if ml:   # learned models replace the rules: winning price from real final bids, sell odds from KPPP outcomes
        floor = s['minBidRate']*1.01
        exp = max(s['rate']*math.exp(ml['mu']), floor)
        s['expRate'] = round(exp); s['expTotal'] = round(exp*billed)
        s['expLo'] = round(max(s['rate']*math.exp(ml['lo']), floor)*billed); s['expHi'] = round(max(s['rate']*math.exp(ml['hi']), floor)*billed)
        s['pSell'] = round(ml['pSell']*100)
        comp = max(0.3, min(5, 0.5*comp + 0.5*(1 + 4*ml['pSell'])))
        s['competition'] = round(comp, 1)
        s['compLabel'] = 'Very high' if comp >= 4.3 else 'High' if comp >= 3.4 else 'Moderate' if comp >= 2.4 else 'Low' if comp >= 1.4 else 'Very low'
    s['expPremium'] = round((exp/s['rate'] - 1)*100)
    # P(win) if you bid our max: rivals' ceilings ~ uniform between min bid and fair_hi
    n_rivals = max(1, round(comp*0.9 - 0.3))
    s['bidders'] = f"{n_rivals + 1}-{n_rivals + 3}"
    span = max(1, fair_hi*0.98 - s['minBidRate'])
    p_each = max(0.02, min(1, (s['maxBidRate'] - s['minBidRate'])/span))
    s['winChance'] = round(100 * p_each**n_rivals)
    if fair_hi*0.98 <= s['minBidRate']:   # overpriced: rivals stop at the minimum too, so it is a tie-break among few bidders
        s['winChance'] = round(100/(n_rivals + 1))
    nbr = (100 - (st or 75)) * (1.6 - comp/4) + (25 if unsold_before else 0)
    if s['baseChange'] is not None and s['baseChange'] <= -10: nbr *= 0.5
    s['noBidRisk'] = round(max(3, min(70, nbr)))
    if ml:
        sig = MODELS['premium']['sigma']
        s['winChance'] = round(100*PHI((math.log(s['maxBidRate']/s['rate']) - ml['mu'])/sig))   # chance the winning price stays under our walk-away
        s['noBidRisk'] = 100 - s['pSell']
    s['stampReg'] = round(s['expTotal']*0.066); s['tds'] = round(s['expTotal']*0.01) if s['expTotal'] > 5e6 else 0
    s['allIn'] = s['expTotal'] + s['stampReg'] + 50000
    s['projectCost'] = s['allIn'] + s['buildCost']
    s['grossYield'] = round(s['rentMonthly']*12/s['projectCost']*100, 2)
    s['value5y'] = round(s['fairTotal'] * (1 + m['cagr']/100)**5)
    s['gain5y'] = round((s['value5y'] - s['allIn'])/s['allIn']*100)
    # yields: rental (residential build), commercial (shop build), resale (5-yr annualised on all-in cost)
    s['rentalYield'] = s['grossYield']
    cmx = s.get('commercial')
    s['commercialYield'] = round(cmx['rent']*12/(s['allIn'] + cmx['build'])*100, 2) if cmx and cmx['gfSqft'] >= 85 else None
    s['resaleReturn'] = round(((s['value5y']/s['allIn'])**(1/5) - 1)*100, 1) if s['allIn'] > 0 and s['value5y'] > 0 else None
    s['projects'] = PROJECTS.get(s['group'], [])
    s['growth'] = dict(label=m['growth'], cagr=m['cagr'], drivers=m['drivers'], watch=m['watch'], story=m['story'], ask=m['ask'])

    # ---------- score (rebuilt) ----------
    if s['status'] == 'withdrawn':
        s['score'] = None; s['verdict'] = 'Withdrawn'
    else:
        s['headroomAtExp'] = round((fair_mid - s['expRate'])/s['expRate']*100, 1)
        value = max(0, min(10, s['headroomAtExp']/3 + 2))   # headroom left after paying the expected winning bid
        growth = {'Slow': 3, 'Slow-steady': 4.5, 'Steady': 6.5, 'Mature': 7, 'Strong': 9}[m['growth']]
        loc = {2: 4.5, 3: 6.5, 4: 8, 5: 9.5}[m['tier']] + (0.5 if s['metro']['km'] < 1.5 else -0.7 if s['metro']['km'] > 5 else 0)
        use = max(0, min(10, f*10 - (1.5 if s['area'] < 60 else 0) + (0.5 if s['area'] >= 150 else 0)))
        allflags = s['flags'] + s['surroundRisks']
        conf = max(0, 10 - sum({'bad': 4, 'warn': 1.5, 'info': 0}[x['sev']] for x in allflags))
        odds = s['winChance']/10
        sc = 0.30*value + 0.15*growth + 0.15*loc + 0.15*use + 0.15*conf + 0.10*odds
        if any(x['sev'] == 'bad' for x in allflags): sc = min(sc, 5.0)
        s['score'] = round(max(0, min(10, sc)), 1)
        s['scoreParts'] = dict(value=round(value, 1), growth=growth, location=round(loc, 1), usability=round(use, 1), confidence=round(conf, 1), odds=round(odds, 1))
        s['verdict'] = ('Strong buy' if s['score'] >= 6.8 else 'Good' if s['score'] >= 5.7 else 'Fair / selective' if s['score'] >= 4.5 else 'Skip / high risk')
    bads = [x for x in s['flags'] + s['surroundRisks'] if x['sev'] == 'bad']
    s['greatFind'] = bool(s['score'] and s['score'] >= 6 and s.get('headroomAtExp', 0) >= 8 and s['winChance'] >= 30 and not bads)
    s['sleeper'] = bool(s['score'] and s['score'] >= 5.5 and s['competition'] <= 2.6 and s['upside'] >= 8 and not bads)

    # ---------- findings that only this site has ----------
    finds = []
    if prev:
        last = prev[-1]
        out = 'went unsold (no bidders)' if last['status'] in UNSOLD else 'closed with a result' if last['status'] in SOLD else 'was listed then cancelled'
        finds.append(f"This exact site was in BDA auction {last['no']} on {last['date']} and {out}, at a base of Rs {last['base']:,.0f}/m². It is back now at Rs {s['rate']:,.0f}/m²." if last.get('base') else f"This exact site was in BDA auction {last['no']} on {last['date']} and {out}.")
        if unsold_before: finds.append(f"Nobody bid on it {unsold_before} time(s) before. That usually means few rivals again, and a real chance of winning near the minimum bid.")
        for p in prev:
            if p.get('final') and p.get('base'):
                finds.append(f"In BDA auction {p['no']} ({p['date']}) this exact site drew a winning bid of Rs {p['final']:,.0f}/m², {round((p['final']/p['base']-1)*100)}% over that round's base, but it is back on sale, so that sale did not complete. It's the best guide to what bidders will pay for this plot.")
        if relisted_after_close: finds.append("Last round closed but the site is back, so the sale did not go through. Usually there was a single bidder (BDA rejects single bids) or the winner failed to pay the 25%. Expect thin competition.")
        if s['baseChange']: finds.append(f"BDA has {'cut' if s['baseChange'] < 0 else 'raised'} the base by {abs(s['baseChange'])}% since last time (Rs {s['prevBase']:,.0f} to Rs {s['rate']:,.0f}/m²).")
        if s['marketCap'] and s['marketCap']['applied']: finds.append(f"Market-tested ceiling: nobody bid at Rs {s['marketCap']['base']:,.0f}/m² on {s['marketCap']['date']}, so we cap fair value at about Rs {s['marketCap']['rate']/SQFT:,.0f}/ft² (that price + 10% + growth since).")
    else:
        finds.append('First time on auction: no BDA bidding history for this exact site.')
    if hs.get('baseSeries') and len(hs['baseSeries']) >= 2:
        (y0, r0), (y1, r1) = hs['baseSeries'][0], hs['baseSeries'][-1]
        finds.append(f"BDA's median base rate in this locality went from Rs {r0:,}/m² ({y0}) to Rs {r1:,}/m² ({y1})" + (f", about {hs['baseCagr']}%/yr." if hs.get('baseCagr') is not None else '.'))
    if hs.get('sellThrough') is not None:
        finds.append(f"In {hs['lots']} past BDA lots here, {hs['sellThrough']}% sold and {100-hs['sellThrough']}% drew no bidders.")
    if g.get('elev'):
        finds.append(f"Ground level is about {g['elev']} m above sea level, with {g['relief']} m of rise and fall within 60 m ({'gentle' if g['slope'] < 3 else 'noticeable' if g['slope'] < 7 else 'steep'} slope, {g['slope']}%).")
    if g.get('frontage'):
        fr = g['frontage']; tg = fr.get('tags', {})
        road = fr.get('name') or {'residential': 'a residential street', 'tertiary': 'a collector road', 'secondary': 'a secondary road', 'primary': 'a main road',
                                  'service': 'a service lane', 'unclassified': 'a local road'}.get(tg.get('highway'), 'a road')
        w = f", mapped {tg['width']} m wide" if tg.get('width') else f", {tg['lanes']} lanes" if tg.get('lanes') else ''
        finds.append(f"Nearest road edge is {fr['m']} m away: {road}{w}.")
    s['findings'] = finds

    # ---------- specific description ----------
    corner_hint = 'trapezoid' if s['irregularity'] >= 0.25 else 'regular rectangle'
    desc = (f"A {s['areaSqft']:,} ft² ({s['area']} m²) {corner_hint} plot, {size_label(s)}, in {s['layout']}. "
            f"{('It faces ' + facing + '. ') if facing else ''}"
            f"Nearest metro: {s['metro']['name']}, {s['metro']['km']} km in a straight line. "
            f"BDA wants Rs {s['ratePerSqft']:,}/ft²; comparable plots here realise Rs {m['lo']:,}-{m['hi']:,}/ft². "
            f"We expect about {s['bidders']} bidders ({s['compLabel'].lower()} competition) and a winning bid near Rs {s['expRate']/SQFT:,.0f}/ft²"
            f" ({'+' if s['expRate'] >= s['rate'] else ''}{(s['expRate']/s['rate']-1)*100:.0f}% over base).")
    s['description'] = desc

    # ---------- buyer personas ----------
    persona = []
    fam_ok = 60 <= s['area'] <= 260 and f >= 0.85 and m['tier'] >= 3
    persona.append(dict(who='Family building a home', fit='Good fit' if fam_ok and not bads else 'Weak fit' if bads or s['area'] < 50 else 'Possible',
        think=f"{'Big enough for a ' + ('3-4 BHK duplex' if s['area'] >= 110 else '2 BHK house') if s['area'] >= 60 else 'Too small for a family home'}. "
              f"{'Water and UGD are still a question in this layout; budget for a borewell and sump.' if s['group'] in ('ANJ', 'FEANJ', 'BSK6T', 'BSK6M', 'BSK6N', 'BSK6O', 'FEBSK') else 'Civic services are in place in most of this area.'} "
              f"{'Schools within a km.' if d('school') < 1000 else 'Check the school run; none mapped within a km.'}"))
    persona.append(dict(who='Rental investor', fit='Good fit' if s['grossYield'] >= 3.2 and s['area'] >= 100 else 'Possible' if s['grossYield'] >= 2.6 else 'Weak fit',
        think=f"Expected gross yield about {s['grossYield']}% on land plus construction. "
              f"{'Strong tenant pool nearby (offices, metro, colleges).' if m['tier'] >= 4 else 'The tenant pool is thinner here; expect longer vacancies.'}"))
    persona.append(dict(who='Land-banker (buy, hold, resell)', fit='Good fit' if m['cagr'] >= 8.5 and s['upside'] >= 10 else 'Possible' if m['cagr'] >= 7 else 'Weak fit',
        think=f"At about {m['cagr']}%/yr the plot could be worth about Rs {s['value5y']/1e5:,.0f} L in 5 years ({s['gain5y']:+}% on all-in cost). "
              f"{'Growth here has been slow; resale takes time and buyers bargain.' if m['growth'] in ('Slow', 'Slow-steady') else 'Resale demand is healthy.'}"))
    if s.get('commercial'):
        cm = s['commercial']
        ok = cm['gfSqft'] >= 85
        persona.insert(0, dict(who='Commercial (shop / kiosk / office)', fit='Good fit' if ok and cm['rent'] >= 12000 else 'Possible' if ok else 'Weak fit',
            think=(f"Sits by a {cm['road']}. After setbacks* about {cm['gfSqft']} ft² of ground-floor shop" + (f" plus {cm['upperSqft']} ft² upstairs" if cm['upperSqft'] else '') +
                   f" is buildable. At ~Rs {cm['rate']}/ft²/month* for small frontage shops here, that rents for about Rs {cm['rent']:,}/month*. Construction about Rs {cm['build']/1e5:.1f} L*. "
                   "Needs: commercial use permitted for this BDA site (RMP zoning on wide roads, plus BDA/GBA approval*), a trade licence, and confirmation the road is not to be widened over the plot.") if ok else
                  f"Next to a {cm['road']}, but too little depth remains after setbacks for a usable shop."))
    s['personas'] = persona

json.dump(dict(sites=sites, history=hist_summary, models={k: v for k, v in (MODELS or {}).items() if k in ('premium', 'sell')}), open(OUT, 'w', encoding='utf8'), ensure_ascii=False)
act = [s for s in sites if s['status'] == 'active']
print('active', len(act), 'kppp linked', sum(1 for s in act if s['kppp']), 'great', sum(s['greatFind'] for s in act), 'sleepers', sum(s['sleeper'] for s in act))
print('repeat sites', sum(1 for s in act if s['prevRounds']))
for g, h in sorted(hist_summary.items()): print(g, h)
from collections import Counter
print(Counter(s['verdict'] for s in sites))
for s in sorted(act, key=lambda s: -s['score'])[:15]:
    print(s['sl'], s['site'], s['group'], s['score'], s['upside'], s['compLabel'], s['winChance'], s['greatFind'], s['geo'].get('facing'))
