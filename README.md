# BDA Auction Desk

**Live: https://bdaauction.vercel.app**

A website that rates every plot in a Bangalore Development Authority (BDA) e-auction. For each site it shows:
- validity checks against BDA's geotag map and corrigendum
- fair value, the likely winning bid and your odds
- bidding history from KPPP
- surroundings and terrain, road width, area growth and upcoming projects
- rental, resale and commercial returns, and how different buyers will see it

It also lists historical BDA auctions collected from KPPP.

- `web/` is the website (Vite, React, TypeScript, Leaflet). It is static and deploys to Vercel.
- `pipeline/` holds the Python scripts that turn one BDA notice into the website's data.

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces fit together.

## KPPP data research

The [4 November 2026 findings](pipeline/tools/kppp_research_2026-11-04.md) document 20 verified public API
routes, a [4,469-notice BDA index](exports/bda_kppp_notice_index_2026-11-04.csv), lot/item details,
corrigenda, pagination corrections, and the limits of live participant counts. See the
[API reference](pipeline/tools/kppp_public_api.md) and [read-only collector](pipeline/tools/collect_kppp_public.ps1).
The research index includes re-listings and non-property auctions; it is not a count of unique plots or
completed sales, and is separate from the website's existing processed data.

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
