"""Per-site surroundings from OpenStreetMap (Overpass) + terrain from SRTM 30 m (OpenTopoData).
Output: {key: {...}} with nearest water/drain/HT line/busy road/etc., road frontage, facing, elevation, slope, aspect."""
import json, math, sys, os, time, subprocess, urllib.request
sites = json.load(open(sys.argv[1], encoding='utf8'))
out, cache = sys.argv[2], sys.argv[3]
os.makedirs(cache, exist_ok=True)
UA = {'User-Agent': 'bda-auction-finder/1.0 (personal research)'}

# one ~3 km box per cluster of sites keeps each Overpass query small
cells = {(round(x['lat']/0.025), round(x['lon']/0.025)) for x in sites}
BOXES = [(a*0.025-0.02, b*0.025-0.02, a*0.025+0.02, b*0.025+0.02) for a, b in sorted(cells)]
Q = """[out:json][timeout:180];(
 way["natural"="water"]({b}); way["water"]({b}); relation["natural"="water"]({b}); way["landuse"="reservoir"]({b});
 way["waterway"~"river|stream|canal|drain|ditch"]({b});
 way["power"~"line|minor_line"]({b});
 way["highway"~"motorway|trunk|primary|secondary|tertiary|residential|unclassified|living_street|service"]({b});
 way["railway"="rail"]({b});
 way["landuse"~"cemetery|landfill|industrial|quarry"]({b}); way["amenity"="grave_yard"]({b});
 nwr["man_made"="wastewater_plant"]({b}); nwr["amenity"="waste_transfer_station"]({b});
 way["leisure"="park"]({b}); way["landuse"~"forest|recreation_ground"]({b}); way["natural"="wood"]({b});
 nwr["amenity"~"school|college|hospital|clinic"]({b});
 nwr["shop"~"supermarket|convenience"]({b});
 node["highway"="bus_stop"]({b});
);out geom;"""

ENDPOINTS = ['https://overpass-api.de/api/interpreter']

def overpass(b):
    """Query one box, rotating mirrors with backoff (curl: some mirrors have TLS chains Python rejects)."""
    f = f"{cache}/osm_{'_'.join(f'{v:.3f}' for v in b)}.json"
    if os.path.exists(f): return json.load(open(f, encoding='utf8'))['elements']
    q = Q.replace('{b}', ','.join(f'{v:.4f}' for v in b))
    for attempt in range(12):
        ep = ENDPOINTS[attempt % len(ENDPOINTS)]
        r = subprocess.run(['curl', '-s', '-m', '120', '-A', UA['User-Agent'], '--data-urlencode', 'data@-', ep],
                           input=q, capture_output=True, text=True, encoding='utf8')
        try:
            data = json.loads(r.stdout)
            open(f, 'w', encoding='utf8').write(r.stdout)
            return data['elements']
        except Exception:
            print('retry', ep, r.stdout[:80].replace(chr(10), ' '), flush=True); time.sleep(min(60, 8 * (attempt + 1)))
    raise SystemExit('Overpass unavailable for box %s' % (b,))

def cat(t):
    w = t.get('waterway'); h = t.get('highway')
    if t.get('natural') == 'water' or 'water' in t or t.get('landuse') == 'reservoir':
        return 'lake'
    if w in ('river', 'canal'): return 'canal'
    if w in ('stream', 'drain', 'ditch'): return 'drain'
    if t.get('power') in ('line',): return 'htline'
    if t.get('power') == 'minor_line': return 'ltline'
    if h in ('motorway', 'trunk', 'primary'): return 'majorroad'
    if h in ('secondary', 'tertiary'): return 'midroad'
    if h == 'bus_stop': return 'bus'
    if h: return 'road'
    if t.get('railway') == 'rail': return 'rail'
    if t.get('landuse') == 'cemetery' or t.get('amenity') == 'grave_yard': return 'cemetery'
    if t.get('landuse') == 'landfill' or t.get('amenity') == 'waste_transfer_station': return 'garbage'
    if t.get('man_made') == 'wastewater_plant': return 'stp'
    if t.get('landuse') == 'industrial': return 'industrial'
    if t.get('landuse') == 'quarry': return 'quarry'
    if t.get('leisure') == 'park' or t.get('landuse') in ('forest', 'recreation_ground') or t.get('natural') == 'wood': return 'green'
    if t.get('amenity') in ('school', 'college'): return 'school'
    if t.get('amenity') in ('hospital', 'clinic'): return 'hospital'
    if t.get('shop'): return 'shop'
    if t.get('highway') == 'bus_stop': return 'bus'
    return None

feats = []
def boxes_needed():
    # use a cached 4 km box when present, otherwise split it into 4 smaller queries (Overpass copes better)
    for b in BOXES:
        f = f"{cache}/osm_{'_'.join(f'{v:.3f}' for v in b)}.json"
        if os.path.exists(f): yield b; continue
        la0, lo0, la1, lo1 = b; mla, mlo = (la0+la1)/2, (lo0+lo1)/2
        for q in ((la0, lo0, mla, mlo), (la0, mlo, mla, lo1), (mla, lo0, la1, mlo), (mla, mlo, la1, lo1)):
            if any(q[0]-0.003 <= x['lat'] <= q[2]+0.003 and q[1]-0.003 <= x['lon'] <= q[3]+0.003 for x in sites):
                yield q

seen = set()
for b in boxes_needed():
    for el in overpass(b):
        if (el['type'], el['id']) in seen: continue
        seen.add((el['type'], el['id']))
        c = cat(el.get('tags', {}))
        if not c: continue
        if el['type'] == 'node': pts = [(el['lat'], el['lon'])]
        elif 'geometry' in el: pts = [(p['lat'], p['lon']) for p in el['geometry']]
        elif 'members' in el: pts = [(p['lat'], p['lon']) for m in el['members'] for p in m.get('geometry', [])]
        else: continue
        if pts: feats.append((c, el.get('tags', {}), pts))
print('features', len(feats))

def xy(lat, lon, lat0, lon0):
    return ((lon-lon0)*111320*math.cos(math.radians(lat0)), (lat-lat0)*110540)

def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx-ax, by-ay; L = dx*dx+dy*dy
    t = 0 if L == 0 else max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/L))
    qx, qy = ax+t*dx, ay+t*dy
    return math.hypot(px-qx, py-qy), (qx, qy)

def nearest(lat, lon, pts):
    P = [xy(a, b, lat, lon) for a, b in pts]
    if len(P) == 1: return math.hypot(*P[0]), P[0]
    best = (1e9, None)
    for i in range(len(P)-1):
        d = seg_dist((0, 0), P[i], P[i+1])
        if d[0] < best[0]: best = d
    return best

def compass(dx, dy):
    ang = (math.degrees(math.atan2(dx, dy)) + 360) % 360
    return ['North', 'North-East', 'East', 'South-East', 'South', 'South-West', 'West', 'North-West'][int((ang+22.5)//45) % 8]

# terrain: centre + 4 points 60 m away, SRTM 30 m
def elev(points):
    res = []
    for i in range(0, len(points), 90):
        chunk = points[i:i+90]
        f = f"{cache}/elev_{abs(hash(tuple(chunk)))}.json"
        if not os.path.exists(f):
            url = 'https://api.opentopodata.org/v1/srtm30m?locations=' + '|'.join(f'{a:.6f},{b:.6f}' for a, b in chunk)
            open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()); time.sleep(1.2)
        res += [r['elevation'] for r in json.load(open(f))['results']]
    return res

D = 60
pts = []
for s in sites:
    dlat, dlon = D/110540, D/(111320*math.cos(math.radians(s['lat'])))
    pts += [(s['lat'], s['lon']), (s['lat']+dlat, s['lon']), (s['lat']-dlat, s['lon']), (s['lat'], s['lon']+dlon), (s['lat'], s['lon']-dlon)]
E = elev(pts)

result = {}
for i, s in enumerate(sites):
    c, n, so, e, w = E[i*5:i*5+5]
    gx, gy = (e-w)/(2*D), (n-so)/(2*D)            # rise per metre to east / north
    slope = math.hypot(gx, gy)*100
    aspect = compass(-gx, -gy) if slope > 0.4 else 'Flat'   # direction the ground falls towards
    near = {}
    for kind, tags, fp in feats:
        if max(abs(fp[0][0]-s['lat']), abs(fp[0][1]-s['lon'])) > 0.05 and len(fp) < 400: continue
        d, q = nearest(s['lat'], s['lon'], fp)
        if kind not in near or d < near[kind]['m']:
            near[kind] = dict(m=round(d), name=tags.get('name') or tags.get('name:en') or '', q=q,
                              tags={k: tags[k] for k in ('highway', 'waterway', 'width', 'lanes', 'voltage', 'surface') if k in tags})
    # road frontage: nearest road of any class
    roads = [near[k] for k in ('road', 'midroad', 'majorroad') if k in near]
    fr = min(roads, key=lambda r: r['m']) if roads else None
    facing = compass(*fr['q']) if fr and fr['m'] < 60 else None
    for v in near.values(): v.pop('q', None)
    if fr: fr = {k: v for k, v in fr.items() if k != 'q'}
    result[s['sl'] + '|' + s['site']] = dict(elev=round(c), slope=round(slope, 1), aspect=aspect, near=near, frontage=fr, facing=facing,
        relief=round(max(n, so, e, w) - min(n, so, e, w)))
json.dump(result, open(out, 'w', encoding='utf8'), ensure_ascii=False)
print('sites', len(result))
