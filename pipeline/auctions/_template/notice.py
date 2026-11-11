"""TEMPLATE for a new BDA e-auction. Copy this folder to auctions/<id>/ (or run `python new_auction.py <id>`),
then fill in the four things marked TODO: the AUCTION facts, the ROWS from the notice PDF, WITHDRAWN, and LOCALITY.
Drop the BDA geotag GeoJSON next to this file as geotag.json. Then run `python run.py <id>`.

notice.py must export exactly these four names: AUCTION, ROWS, WITHDRAWN, LOCALITY (sites.py imports them)."""

# TODO(1) — auction facts. id must equal the folder name. Dates ISO (YYYY-MM-DD). slots map sl-number ranges to a bid day.
AUCTION = dict(
    id='TODO',                      # e.g. 't16' — MUST match the auctions/<id>/ folder name
    code='TODO',                    # e.g. 'T-16'
    title='BDA e-auction T-16/2026-27',
    notice='BDA/EM/e-Auction/T-16/2026-27',
    noticeDate='2026-00-00',
    eoiDeadline='2026-00-00T17:00:00+05:30',
    status='upcoming',              # 'upcoming' -> 'bidding' -> 'closed'
    bidDays=[                        # one entry per bidding day, shown on the site
        dict(date='2026-00-00', range='Sl 1-??'),
    ],
    slots=[                          # (first_sl, last_sl, 'YYYY-MM-DD') — which sl-numbers bid on which day
        (1, 999, '2026-00-00'),
    ],
    emd=400000, fee=500, minBidUplift=0.10,
    notice_pdf='https://www.bdakarnataka.in/...TODO',
    corrigendum_pdf='',             # '' if none
    geotag_url='http://106.51.29.213/',   # BDA geotag map; export its GeoJSON to geotag.json in this folder
    kppp='https://kppp.karnataka.gov.in/#/portal/Auctions/live',
    helpline='9483166622',
    corrections={},                 # corrigendum area changes: {'<sl>': new_area_m2}
)

# TODO(2) — ROWS from the notice PDF, one site per line, pipe-delimited:
#   sl | site | layout | EW | NS | area_sqm | base_rate_per_sqm | zone | locality_group
# EW/NS accept simple expressions like [7.50+3.10]/2 or (15.00+28.00)/2 (averaged frontages).
# A row whose sl starts with 'C' was added by a corrigendum. 'zone' is South/West/North.
# 'locality_group' must be a key in market.py MARKET (e.g. ANJ, BSK6O, ARKT) — add it to MARKET first if new.
ROWS = """
"""   # TODO: paste rows here, e.g.  1|711|Anjanapura Township, 1st Block, Anjanapura|[7.50+3.10]/2|12.00|63.60|73000|South|ANJ

# TODO(3) — sl-numbers withdrawn before/at auction (BDA removes some). Empty set if none.
WITHDRAWN = set()

# TODO(4) — approx coords for sites missing from the BDA geotag map: layout_string -> (lat, lon, 'note').
# Leave empty at first; `run.py` prints which sites were not matched so you can add them here.
LOCALITY = {}
