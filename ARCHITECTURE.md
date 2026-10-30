# Architecture

```mermaid
flowchart LR
  subgraph Sources
    N[BDA notice + corrigendum PDFs]
    G[BDA geotag map GeoJSON]
    K[KPPP portal API<br/>current lots + 2,742 past lots]
    O[OpenStreetMap / Overpass]
    T[SRTM 30 m via OpenTopoData]
    R[BBMP road-width map KML]
    M[Market research<br/>market.py, projects.py]
  end
  subgraph pipeline [pipeline/ - Python]
    A[analyze.py<br/>validity, geotag match]
    KP[kppp.py / kppp_history.py]
    E[enrich.py<br/>surroundings, terrain, facing]
    RW[roadwidth.py]
    I[insights.py<br/>fair value, bids, odds, rating]
    X[export.py]
  end
  subgraph web [web/ - React static site]
    D[(public/data<br/>sites.json, meta.json)]
    UI[Home · Explore · Site · Localities · Shortlist · Method]
  end
  N --> A
  G --> A
  K --> KP --> I
  A --> E --> I
  O --> E
  T --> E
  R --> RW --> I
  M --> I
  A --> I --> X --> D --> UI
  UI -->|deploy| V[Vercel]
```

## Why this shape
- **Static site, precomputed data.** The auction changes a few times a year, so all analysis runs offline in Python, and the browser only reads two JSON files (about 200 KB gzipped). There is no server to run, Vercel hosting is free, and it's fast on phones.
- **Pipeline is re-runnable per auction.** Only `sites.py` (the notice rows) needs hand edits for a new auction. Everything else is fetched or derived.
- **Every estimate is labelled.** Model outputs are marked `*` in the UI. Missing inputs are estimated and never scored as a negative.

## Pipeline stages
| Script | Input | Output |
|---|---|---|
| `analyze.py` | notice rows (`sites.py`), geotag GeoJSON | `data.json`: validity flags, geotag match, base pricing |
| `kppp.py` | KPPP search API | `kppp_live.json`: auction notice number per site |
| `kppp_history.py` | KPPP search + view APIs | `kppp_history.json`: past lots (status, base rate, date) |
| `enrich.py` | Overpass, OpenTopoData | `geo_extra.json`: nearest lake, drain, HT line, roads, etc.; elevation, slope, facing |
| `roadwidth.py` | BBMP road-width KML, OSM tags | `roads.json`: road width (mapped or estimated*), planned RMP width, FAR |
| `insights.py` | all of the above + `market.py`, `projects.py` | `data2.json`: fair value, likely bid, odds, yields, rating, findings, personas |
| `export.py` | `data2.json` | `web/public/data/sites.json`, `meta.json` |

## Models (summary)
- **Fair value** = locality realisable rate × usability × facing/road adjustment, capped by any earlier no-bid price (+10%, grown). Small plots on wide roads use the higher of residential value and shop-rent value.
- **Likely winning bid** = base × (1 + 10% … 65% by competition), calibrated to BDA's Dec 2021 result (+62% average over base), capped at the top of the resale range.
- **Competition** = locality demand, adjusted by BDA sell-through (KPPP), ticket size, usability, earlier no-bid rounds and re-listing.
- **Rating** = 30% value after the likely bid + 15% growth + 15% location + 15% usability + 15% confidence + 10% win odds; a serious red flag caps it at 5.

## Web app
- `src/lib/`: types, data loading (context), filters (URL-synced), rankings, shortlist (localStorage).
- `src/pages/`: Home (picks by ranking), Explore (filters, list and map, mobile list/map switch), SitePage (sectioned report, rent calculator), Localities, Shortlist and compare, Method.
- Maps: Leaflet with Esri World Imagery (satellite) and OpenStreetMap tiles. Both are free and need no API key.
- `vercel.json`: SPA rewrites and data caching.
