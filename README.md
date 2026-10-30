# BDA Auction Desk

**Live: https://bdaauction.vercel.app**

A website that rates every plot in a Bangalore Development Authority (BDA) e-auction. For each site it shows:
- validity checks against BDA's geotag map and corrigendum
- fair value, the likely winning bid and your odds
- bidding history from KPPP
- surroundings and terrain, road width, area growth and upcoming projects
- rental, resale and commercial returns, and how different buyers will see it

It also lists every past BDA auction round on KPPP.

- `web/` is the website (Vite, React, TypeScript, Leaflet). It is static and deploys to Vercel.
- `pipeline/` holds the Python scripts that turn one BDA notice into the website's data.

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces fit together.

## Run the website locally
```
cd web
npm install
npm run dev        # http://localhost:5180
```

## Add a new auction
1. Create `pipeline/auctions/<id>/notice.py`, copied from `auctions/t15/notice.py`. Set `AUCTION` (code, dates, PDFs, bid-day slots) and `ROWS` (one line per site from the notice PDF). Add any `WITHDRAWN` serials from the corrigendum.
2. Save BDA's geotag GeoJSON as `pipeline/auctions/<id>/geotag.json`. The geotag page at http://106.51.29.213/ embeds it as `const data=...`.
3. If BDA lists a new locality, add it to `pipeline/market.py` and `pipeline/projects.py`.
4. Run the pipeline:
   ```
   cd pipeline
   python run.py <id>
   ```
   This writes `web/public/data/<id>/` and adds the auction to `web/public/data/auctions.json`. The newest auction becomes the default on the site.
5. Commit and push. Vercel redeploys automatically.

Decision support only, not a valuation or legal opinion.
