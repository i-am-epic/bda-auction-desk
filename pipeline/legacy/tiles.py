"""Download free, keyless basemap tiles around the auction sites and pack them as base64
(artifact pages can't fetch external images). Two layers: OpenStreetMap streets + Esri World Imagery satellite."""
import json, math, sys, base64, urllib.request, os, time, io
from PIL import Image
sites = json.load(open(sys.argv[1], encoding='utf8'))
out = sys.argv[2]
cache = sys.argv[3]
PROVIDERS = {
    'osm': ('https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'image/png', 16),
    'sat': ('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'image/jpeg', 17),
}
QUALITY = {'osm': 72, 'sat': 55}
UA = {'User-Agent': 'bda-auction-finder/1.0 (personal research; one-off download)'}

def tile(lat, lon, z):
    n = 2**z; x = int((lon+180)/360*n)
    y = int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n); return x, y

def wanted(maxz):
    need = set()
    lats = [s['lat'] for s in sites]; lons = [s['lon'] for s in sites]
    for z in (11, 12, 13):
        x0, y0 = tile(max(lats)+0.02, min(lons)-0.02, z); x1, y1 = tile(min(lats)-0.02, max(lons)+0.02, z)
        need |= {(z, x, y) for x in range(x0, x1+1) for y in range(y0, y1+1)}
    for z, r in ((14, 1), (15, 0), (16, 0), (17, 0)):
        if z > maxz: continue
        for s in sites:
            x, y = tile(s['lat'], s['lon'], z)
            need |= {(z, x+dx, y+dy) for dx in range(-r, r+1) for dy in range(-r, r+1)}
    return need

packed = {}
for name, (url, mime, maxz) in PROVIDERS.items():
    os.makedirs(f'{cache}/{name}', exist_ok=True)
    layer = {}
    for z, x, y in sorted(wanted(maxz)):
        f = f'{cache}/{name}/{z}_{x}_{y}'
        if not os.path.exists(f):
            data = urllib.request.urlopen(urllib.request.Request(url.format(z=z, x=x, y=y), headers=UA), timeout=30).read()
            open(f, 'wb').write(data); time.sleep(0.1)
        buf = io.BytesIO()  # re-encode as WebP to keep the single-file page under the 16 MB artifact limit
        Image.open(f).convert('RGB').save(buf, 'WEBP', quality=QUALITY[name], method=6)
        layer[f'{z}/{x}/{y}'] = base64.b64encode(buf.getvalue()).decode()
    packed[name] = {'mime': 'image/webp', 'tiles': layer}
    print(name, len(layer), 'tiles')
json.dump(packed, open(out, 'w'))
print('bytes', os.path.getsize(out))
