"""Place plots that BDA's geotag map lacks, as accurately as the evidence allows.
Order of evidence:
  1. A per-site pin from bdaeauction.in (their pins match BDA polygon centres to a median 1.7 m, so they come from BDA geotag data).
  2. Adjacent to the nearest-numbered officially mapped site in the same block, rotated to that block's grid, on the side
     that keeps clear of OpenStreetMap road centrelines and other plots.
  3. The locality point, nudged off any road.
Usage: python place.py build/data.json build/bdae_pins.json <osm-cache-dir>   (rewrites data.json in place)"""
import json, math, re, sys, glob, os

data_p, pins_p, cache = sys.argv[1:4]
sites = json.load(open(data_p, encoding='utf8'))
pins = json.load(open(pins_p, encoding='utf8'))
ROADS = ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'living_street', 'service')

roads = []
for f in glob.glob(os.path.join(cache, 'osm_*.json')):
    for el in json.load(open(f, encoding='utf8')).get('elements', []):
        if el.get('type') == 'way' and el.get('tags', {}).get('highway') in ROADS and 'geometry' in el:
            roads.append([(p['lat'], p['lon']) for p in el['geometry']])
print('road lines', len(roads))

def words(t):
    t = t.upper().replace('ARKAVATHY', 'ARKAVATHI').replace('FURTHER EXTENSION OF', 'FE OF').replace('GANAKALLLU', 'GANAKALLU')
    return {w for w in re.findall(r'[A-Z0-9]+', t) if w not in {'OF', 'LAYOUT', 'BLOCK', 'STAGE', 'THE', 'AND', 'VILLAGE'}}

def pin_for(s):
    best = None
    for p in pins:
        if not p['title'].startswith(f"Site {s['site']} |"): continue
        sc = len(words(p['title'].split('|')[1]) & words(s['layout'])) / max(1, len(words(s['layout'])))
        if best is None or sc > best[0]: best = (sc, p)
    return (best[1]['lat'], best[1]['lon']) if best and best[0] >= 0.6 else None

# --- local metric frame helpers
def to_xy(lat, lon, o): return ((lon - o[1]) * 111320 * math.cos(math.radians(o[0])), (lat - o[0]) * 110540)
def to_ll(x, y, o): return [o[0] + y / 110540, o[1] + x / (111320 * math.cos(math.radians(o[0])))]
def rot(p, a): c, s_ = math.cos(a), math.sin(a); return (p[0]*c - p[1]*s_, p[0]*s_ + p[1]*c)
def seg_d(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; L = dx*dx + dy*dy
    t = 0 if L == 0 else max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / L))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))

def avg(expr):
    e = expr.replace('[', '(').replace(']', ')').strip(); e = re.sub(r'\)\s*2$', ')/2', e)
    try: return float(eval(e, {'__builtins__': {}})) if re.fullmatch(r'[0-9.+*/() ]+', e) else None
    except Exception: return None
def pair(expr):
    m = re.match(r'\(\s*([\d.]+)\s*\+\s*([\d.]+)\s*\)', expr.replace('[', '(').replace(']', ')'))
    return (float(m.group(1)), float(m.group(2))) if m else None

def shape(s):
    """Plot outline in metres, centred on 0,0, x = east, y = north, from the notice dimensions."""
    a, b = avg(s['ew']), avg(s['ns'])
    if s['sl'] == '23': a, b = 18, 1.75          # 255/L: triangle 18 m long, 3.5 m deep
    if not (a and b): a = b = math.sqrt(s['area'])
    ew, ns = pair(s['ew']), pair(s['ns'])
    if s['sl'] == '23': return [(-9, -1.75), (9, -1.75), (9, 1.75)], 18, 3.5
    if ew: p, q = ew; return [(-p/2, b/2), (p/2, b/2), (q/2, -b/2), (-q/2, -b/2)], max(p, q), b
    if ns: p, q = ns; return [(-a/2, -p/2), (-a/2, p/2), (a/2, q/2), (a/2, -q/2)], a, max(p, q)
    return [(-a/2, -b/2), (-a/2, b/2), (a/2, b/2), (a/2, -b/2)], a, b

def grid_angle(poly_ll, o):
    """Rotation of a mapped plot: angle of its longest edge, folded to [-45, 45] degrees."""
    P = [to_xy(la, lo, o) for la, lo in poly_ll]
    best = max(((math.hypot(P[i+1][0]-P[i][0], P[i+1][1]-P[i][1]), math.atan2(P[i+1][1]-P[i][1], P[i+1][0]-P[i][0])) for i in range(len(P)-1)))
    a = best[1]
    while a > math.pi/4: a -= math.pi/2
    while a < -math.pi/4: a += math.pi/2
    return a

def clearance(pts_xy, o, others_xy):
    """Smallest distance (m) from the plot's corners and centre to any road centreline; also overlap with other plots."""
    probe = pts_xy + [(sum(p[0] for p in pts_xy)/len(pts_xy), sum(p[1] for p in pts_xy)/len(pts_xy))]
    dmin = 99.0
    for r in roads:
        if abs(r[0][0] - o[0]) > 0.006 and abs(r[-1][0] - o[0]) > 0.006: continue
        R = [to_xy(la, lo, o) for la, lo in r]
        for p in probe:
            for i in range(len(R)-1):
                dmin = min(dmin, seg_d(p, R[i], R[i+1]))
    c = probe[-1]
    overlap = any(math.hypot(c[0]-q[0], c[1]-q[1]) < 4 for q in others_xy)
    return dmin, overlap

num = lambda t: int(re.sub(r'\D', '', t) or 0)
official = [s for s in sites if s.get('geotag') == 'official']
placed_centres = [(s['lat'], s['lon']) for s in official]
stats = {}
for s in sites:
    if s.get('geotag') != 'approx': continue
    o = (s['lat'], s['lon'])
    pts, W, H = shape(s)
    pin = pin_for(s)
    sib = sorted([x for x in official if x['layout'] == s['layout']], key=lambda x: (abs(num(x['site']) - num(s['site'])), 0))
    if pin:
        o = pin
        near = min(official, key=lambda x: (x['lat']-o[0])**2 + (x['lon']-o[1])**2)
        ang = grid_angle(near['polygon'], o) if math.hypot((near['lat']-o[0])*110540, (near['lon']-o[1])*111320) < 300 else 0
        centre = (0.0, 0.0)
        method = 'pin'; note = 'Located by a per-site pin from bdaeauction.in (their pins match BDA geotag polygons within ~2 m); outline drawn from the notice dimensions*'
    elif sib:
        nb = sib[0]; o = (nb['lat'], nb['lon'])
        ang = grid_angle(nb['polygon'], o)
        NB = [rot(to_xy(la, lo, o), -ang) for la, lo in nb['polygon'][:-1]]
        hw = (max(p[0] for p in NB) - min(p[0] for p in NB)) / 2; hh = (max(p[1] for p in NB) - min(p[1] for p in NB)) / 2
        others = [rot(to_xy(la, lo, o), -ang) for la, lo in placed_centres]
        best = None
        for cx, cy in ((hw + W/2 + 0.3, 0), (-(hw + W/2 + 0.3), 0), (0, hh + H/2 + 0.3), (0, -(hh + H/2 + 0.3))):
            cand = [rot((x + cx, y + cy), ang) for x, y in pts]
            dmin, ov = clearance(cand, o, [rot(q, ang) for q in others])
            score = min(dmin, 12) - (20 if ov else 0)
            if best is None or score > best[0]: best = (score, (cx, cy), dmin)
        centre = rot(best[1], ang)
        method = 'adjacent'; note = (f"Not on BDA's map. Placed beside Site {nb['site']} (nearest site number mapped in this block), on the side clear of roads "
                                     f"(~{best[2]:.0f} m from the nearest road centreline)*")
    else:
        ang = 0; best = None
        for r in range(0, 70, 6):
            for k in range(max(1, r // 3 * 4) if r else 1):
                t = 2*math.pi*k / max(1, r // 3 * 4)
                c = (r*math.cos(t), r*math.sin(t))
                dmin, ov = clearance([(x + c[0], y + c[1]) for x, y in pts], o, [to_xy(la, lo, o) for la, lo in placed_centres])
                if dmin >= 6 and not ov: best = c; break
            if best: break
        centre = best or (0.0, 0.0)
        method = 'locality'; note = s.get('geoNote', 'Approximate') + '; nudged off the nearest road*'
    poly = [to_ll(*(lambda p: (p[0] + centre[0], p[1] + centre[1]))(rot(p, ang)), o) for p in pts]
    poly.append(poly[0])
    c = to_ll(centre[0], centre[1], o)
    s.update(lat=c[0], lon=c[1], polygon=poly, polyDrawn=True, placement=method, geoNote=note)
    placed_centres.append((c[0], c[1]))
    stats[method] = stats.get(method, 0) + 1
    print(s['sl'], s['site'], method, note[:90])
json.dump(sites, open(data_p, 'w', encoding='utf8'), ensure_ascii=False)
print(stats)
