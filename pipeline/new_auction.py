"""Scaffold a new auction from auctions/_template/.

    python new_auction.py t16      # creates auctions/t16/ from the template, then prints the checklist

It copies the template folder, sets AUCTION['id'] to the new id, and refuses if the folder already exists.
Fill in the TODOs in auctions/<id>/notice.py, drop the BDA geotag GeoJSON as auctions/<id>/geotag.json,
then run `python run.py <id>`."""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) != 2 or not re.fullmatch(r'[a-z0-9]+', sys.argv[1]):
    sys.exit('usage: python new_auction.py <id>   (lowercase letters/digits, e.g. t16)')
aid = sys.argv[1]
src = os.path.join(HERE, 'auctions', '_template')
dst = os.path.join(HERE, 'auctions', aid)
if os.path.exists(dst):
    sys.exit(f'auctions/{aid}/ already exists — refusing to overwrite.')
if not os.path.isdir(src):
    sys.exit('auctions/_template/ is missing.')

shutil.copytree(src, dst)
# set AUCTION id to the new folder name so it can't drift from the directory
np = os.path.join(dst, 'notice.py')
txt = open(np, encoding='utf8').read().replace("id='TODO',", f"id='{aid}',", 1)
open(np, 'w', encoding='utf8').write(txt)

print(f"""created auctions/{aid}/  (id set to '{aid}')

next:
  1. auctions/{aid}/notice.py  — fill the 4 TODOs: AUCTION facts, ROWS (from the notice PDF),
     WITHDRAWN, LOCALITY. Add any new locality_group to market.py MARKET first.
  2. auctions/{aid}/geotag.json — replace with the BDA geotag GeoJSON (from the notice's geotag map).
  3. python run.py {aid}        — runs the whole pipeline and publishes web/public/data/{aid}/.
  4. after bidding closes, add auctions/{aid}/results.json (sold / no-bids) the way t15 has it.""")
