"""Run the whole pipeline for one auction and publish it to the website.

    python run.py t15                 # everything (KPPP + OSM fetches are cached)
    python run.py t15 --skip-fetch    # reuse KPPP / OSM / terrain data already in build/<id>/

Inputs per auction live in auctions/<id>/: notice.py (rows + dates) and geotag.json (BDA geotag GeoJSON).
Shared inputs in inputs/: bdae_pins.json (per-site pins), roadwidth.kml (BBMP road widths).
Output: ../web/public/data/<id>/{sites,meta}.json, ../web/public/data/auctions.json and history.json."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
aid = sys.argv[1] if len(sys.argv) > 1 else 't15'
skip = '--skip-fetch' in sys.argv
B = os.path.join(HERE, 'build', aid)
A = os.path.join(HERE, 'auctions', aid)
I = os.path.join(HERE, 'inputs')
CACHE = os.path.join(HERE, 'build', '_cache')
WEB = os.path.join(HERE, '..', 'web', 'public', 'data')
os.makedirs(B, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
env = dict(os.environ, AUCTION=aid)

def step(name, *args, fetch=False):
    if fetch and skip and os.path.exists(next(a for a in args[1:] if a.endswith('.json'))):
        print(f'· {name}: cached'); return
    print(f'▶ {name}', flush=True)
    subprocess.run([sys.executable, '-X', 'utf8', '-I', os.path.join(HERE, args[0]), *args[1:]], check=True, env=env)

p = lambda *x: os.path.join(B, *x)
KML = os.path.join(I, 'roadwidth.kml')
if not os.path.exists(KML):   # 25 MB, not kept in git
    print('▶ downloading BBMP road-width map (OpenCity)')
    subprocess.run(['curl', '-sSL', '-o', KML, 'https://data.opencity.in/dataset/0a72695d-0c48-4442-b8ee-e2a24b157d66/resource/'
                    'bd9d5ea1-40c8-4699-87c9-d4a4f303cfff/download/ed239bef-1bf5-4926-8621-2fd84c7db3d0.kml'], check=True)
step('validity & geotag', 'analyze.py', os.path.join(A, 'geotag.json'), p('data.json'))
step('place untagged plots', 'place.py', p('data.json'), os.path.join(I, 'bdae_pins.json'), CACHE)
step('KPPP lots (this round)', 'kppp.py', p('kppp_live.json'), 'PUBLISHED', fetch=True)
step('KPPP history (all past BDA lots)', 'kppp_history.py', p('kppp_history.json'), fetch=True)
step('surroundings & terrain', 'enrich.py', p('data.json'), p('geo_extra.json'), CACHE)
step('road widths', 'roadwidth.py', KML, p('data.json'), p('geo_extra.json'), p('roads.json'))
step('real winning bids', 'fetch_results.py', os.path.join(I, 'bid_results.json'), fetch=True)
step('ingest real KPPP bids', 'ingest_kppp.py', os.path.join(HERE, 'private', 'kppp_bids.jsonl'), os.path.join(I, 'kppp_finals.json'))
step('learn sell odds + winning price', 'models.py', os.path.join(I, 'bid_results.json'), p('kppp_history.json'), p('data.json'), p('models.json'))
step('pricing, odds, rating', 'insights.py', p('data.json'), p('geo_extra.json'), p('kppp_history.json'), p('kppp_live.json'), p('data2.json'), p('roads.json'), p('models.json'))
step('export to website', 'export.py', p('data2.json'), WEB)
step('past auctions page', 'export_history.py', p('kppp_history.json'), WEB)
step('lot history spreadsheet', 'export_lots_csv.py', p('kppp_history.json'), os.path.join(I, 'bid_results.json'), os.path.join(WEB, 'downloads', 'bda_kppp_lot_history.csv'))
import shutil; shutil.copy(os.path.join(HERE, '..', 'exports', 'bda_real_final_bids.csv'), os.path.join(WEB, 'downloads', 'bda_real_final_bids.csv'))
print('done:', aid)
