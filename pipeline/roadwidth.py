"""Road widths per site.
Source 1 (measured): BBMP road width map via OpenCity (KML, 23k segments): RR_width_B = existing width (m), RR_WIDTH_P = RMP proposed width (m).
Source 2 (estimated): OSM width/lanes tags, else OSM road class + BDA layout norms from plot size.
Usage: python roadwidth.py <roadwidth.kml> build/data.json build/geo_extra.json build/roads.json"""
import json, math, re, sys

kml, data_p, geo_p, out = sys.argv[1:5]
sites = json.load(open(data_p, encoding='utf8'))
geo = json.load(open(geo_p, encoding='utf8')) if geo_p != '-' else {}

segs = []
txt = open(kml, encoding='utf8', errors='ignore').read()
for pm in re.finditer(r'<Placemark>(.*?)</Placemark>', txt, re.S):
    b = pm.group(1)
    def f(n):
        m = re.search(r'<SimpleData name="%s">([^<]*)</SimpleData>' % re.escape(n), b)
        return m.group(1) if m else None
    coords = []
    for c in re.findall(r'<coordinates>(.*?)</coordinates>', b, re.S):
        coords += [tuple(map(float, p.split(',')[:2])) for p in c.split()]
    if coords:
        segs.append(dict(ex=f('RR_width_B'), prop=f('RR_WIDTH_P'), hier=f('RR_TP_HIER'), pts=coords))
print('segments', len(segs))

def xy(lat, lon, lat0, lon0): return ((lon-lon0)*111320*math.cos(math.radians(lat0)), (lat-lat0)*110540)
def segd(p, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx-ax, by-ay; L = dx*dx+dy*dy
    t = 0 if L == 0 else max(0, min(1, ((p[0]-ax)*dx+(p[1]-ay)*dy)/L))
    return math.hypot(p[0]-(ax+t*dx), p[1]-(ay+t*dy))

def num(v):
    try:
        x = float(v); return x if x > 0 else None
    except (TypeError, ValueError): return None

CLASS = {'primary': (24, 30), 'trunk': (30, 45), 'secondary': (18, 24), 'tertiary': (12, 18),
         'residential': (9, 12), 'unclassified': (9, 12), 'living_street': (6, 9), 'service': (6, 9)}

res = {}
for s in sites:
    k = s['sl'] + '|' + s['site']
    best = None
    for g in segs:
        lon0, lat0 = g['pts'][0]
        if abs(lat0 - s['lat']) > 0.03 or abs(lon0 - s['lon']) > 0.03: continue
        P = [xy(la, lo, s['lat'], s['lon']) for lo, la in g['pts']]
        d = min(segd((0, 0), P[i], P[i+1]) for i in range(len(P)-1)) if len(P) > 1 else math.hypot(*P[0])
        if best is None or d < best[0]: best = (d, g)
    r = {}
    # BBMP layer = RMP *planned* right-of-way (RR_WIDTH_P); RR_width_B is its half-width buffer, not today's width
    if best and num(best[1]['prop']):
        d, g = best; half = num(g['ex']) or num(g['prop'])/2
        if d <= half + 15:
            r['planned'] = dict(width=num(g['prop']), dist=round(d), inside=d < half,
                                source='BBMP / RMP road width map (OpenCity)')
    fr = (geo.get(k) or {}).get('frontage') or {}
    tg = fr.get('tags', {})
    w = num(re.sub(r'[^0-9.]', '', tg.get('width', '')) if tg.get('width') else None)
    if w and fr.get('m', 99) < 40:
        r.update(width=w, source='OpenStreetMap width tag', conf='Mapped')
    elif tg.get('lanes') and fr.get('m', 99) < 40:
        r.update(width=round(float(tg['lanes'])*3.5 + 2, 1), source='OpenStreetMap lane count x 3.5 m + verges', conf='Estimated*')
    else:
        a = s['area']
        lo, hi = (6, 9) if a < 60 else (9, 12) if a < 250 else (12, 18)
        if tg.get('highway') in CLASS and fr.get('m', 99) < 40:
            lo, hi = CLASS[tg['highway']] if CLASS[tg['highway']][0] > hi else (lo, hi)
            src = f"Estimated* from the OSM road class ({tg['highway']}) and BDA layout norms for a {a:.0f} m² site"
        else:
            src = f"Estimated* from BDA layout norms for a {a:.0f} m² site"
        r.update(width=round((lo+hi)/2, 1), range=[lo, hi], source=src, conf='Estimated*')
    w = r['width']
    r['ft'] = round(w*3.28)
    # FAR by abutting road width (Bengaluru zoning, conservative): < 12 m -> 1.75; 12-18 m -> 2.25; >= 18 m -> 2.5
    r['far'] = 1.75 if w < 12 else 2.25 if w < 18 else 2.5
    res[k] = r
json.dump(res, open(out, 'w', encoding='utf8'), ensure_ascii=False)
from collections import Counter
print(Counter(v['conf'] for v in res.values()))
print([(k, v['planned']) for k, v in res.items() if v.get('planned')])
