# Adding the next auction

One folder per auction: `auctions/<id>/`. Each holds `notice.py` (the transcribed notice),
`geotag.json` (BDA's site polygons), and — after bidding — `results.json` (sold / no-bids outcomes).

## Steps when a new notice (e.g. T-16) is published

1. **Scaffold it**
   ```
   python new_auction.py t16
   ```
   This copies `auctions/_template/` → `auctions/t16/` and sets `AUCTION['id']='t16'`.

   **Auto-fill shortcut:** `python fetch_bda.py t16` pulls the BDA geotag map (`http://106.51.29.213/`, which
   embeds a GeoJSON with Sl_No, Site_No, Layout, dimensions, Area, Division + polygons), joins it to KPPP for
   base rates and dates, writes `auctions/t16/geotag.json`, and prints a ready `ROWS` block to paste. It needs
   the geotag server to be serving that auction (BDA switches it per round) — until then, transcribe by hand.
   Spot-check the base rates it fills: site numbers recur across sub-blocks, so a few may need a manual fix.

2. **Fill `auctions/t16/notice.py`** — the four TODOs:
   - `AUCTION` facts: code, title, notice no., dates, `bidDays`/`slots`, EMD/fee, notice & corrigendum PDF URLs, `geotag_url`.
   - `ROWS`: one site per line from the notice PDF — `sl | site | layout | EW | NS | area_sqm | base_rate | zone | group`.
     `group` must exist in `market.py` `MARKET`; add the locality there first if it's new.
   - `WITHDRAWN`: sl-numbers BDA pulls before auction.
   - `LOCALITY`: approx coords for sites missing from the geotag map (run once; it prints the unmatched ones).

3. **Drop the geotag** — export the GeoJSON from the notice's BDA geotag map (`geotag_url`, e.g. `http://106.51.29.213/`)
   and save it as `auctions/t16/geotag.json`.

4. **Run it**
   ```
   python run.py t16
   ```
   Publishes `web/public/data/t16/{sites,meta}.json` and updates `auctions.json` + `history.json`.
   The website serves it automatically at `/a/t16/…` (newest auction is the default).

5. **After bidding closes** — collect each lot's KPPP public status (BIDDING_CLOSED = sold, NO_PARTICIPATIONS /
   NO_BIDS_RECEIVED = no bids) into `auctions/t16/results.json`, keyed by **notice number** (site numbers aren't
   unique across layouts). `export.py` reads it and marks Sold / No-bids in the UI. Then re-run `run.py t16`.
   Refreshing the KPPP history before the run also folds the new outcomes into the sell-odds model.

`_template/` is ignored by the pipeline (the default auction is `t15`); it exists only to be copied.
