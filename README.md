# BDA Auction Desk

A website that rates every plot in a Bangalore Development Authority (BDA) e-auction. For each site it shows validity checks, fair value, the likely winning bid and odds, bidding history from KPPP, surroundings and terrain, road width, area growth, upcoming projects, rental, resale and commercial returns, and how different buyers will see it.

- `web/`: the website (Vite + React + TypeScript + Leaflet). Static, deployed to Vercel.
- `pipeline/`: Python scripts that turn BDA's notice into the site's data (`web/public/data/*.json`).

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces fit and how to run a new auction.

## Run the website locally
```
cd web
npm install
npm run dev        # http://localhost:5180
```

## Refresh the data for a new auction
```
cd pipeline
python analyze.py <geotag.json> build/data.json
python kppp.py build/kppp_live.json PUBLISHED
python kppp_history.py build/kppp_history.json
python enrich.py build/data.json build/geo_extra.json <cache-dir>
python roadwidth.py <roadwidth.kml> build/data.json build/geo_extra.json build/roads.json
python insights.py build/data.json build/geo_extra.json build/kppp_history.json build/kppp_live.json build/data2.json build/roads.json
python export.py build/data2.json ../web/public/data
```
Then commit and push. Vercel redeploys automatically.

Decision support only, not a valuation or legal opinion.
