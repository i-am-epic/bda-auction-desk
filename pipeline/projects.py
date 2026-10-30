# Upcoming projects (boosts) and concerns per locality, researched 30 Oct 2026. Timelines from news reports; marked * where unconfirmed.
# kind: 'boost' raises long-term value, 'concern' is something a buyer should check or price in.
S_METRO = 'https://www.nativeplanet.com/news/bengaluru-metro-update-2026-blue-line-deadlines-pink-line-opening-orr-traffic-011-23813.html'
S_BBC = 'https://www.propnewz.com/blog/bengaluru-business-corridor-prr-package-1-loa-buyer-2026-06-07'
S_BBC_LAND = 'https://urbanacres.in/bengaluru-business-corridor-shows-why-land-is-the-real-bottleneck/'
S_GBA = 'https://newsable.asianetnews.com/karnataka-news/bda-transfers-8-developed-layouts-to-greater-bengaluru-authority-articleshow-fymlv0m'
S_UGD = 'https://www.deccanherald.com/india/karnataka/bengaluru/rs-55-cr-released-for-ugd-in-banashankari-6th-stage-1122561.html'
S_WATER = 'https://www.thehansindia.com/karnataka/bengaluru-20-years-on-banashankari-6th-stage-bda-layout-cries-for-basic-amenities-740919'
S_ARK = 'https://www.talkinglands.com/blogs/arkavathy-layout-bda-complete-guide'
S_ROADS = 'https://tradebrains.in/money/bengaluru-traffic-relief-10-major-road-projects-expected-to-open-in-2026/'
S_SETBACK = 'https://www.thehansindia.com/news/cities/bengaluru/setback-norms-relaxed-for-small-plots-as-gba-issues-final-notification-1037910'
S_FAR = 'https://corporate.cyrilamarchandblogs.com/2026/07/bengaluru-goes-vertical-green-light-to-premium-far/'

def P(kind, name, status, effect, src):
    return dict(kind=kind, name=name, status=status, effect=effect, src=src)

GBA_HANDOVER = P('boost', 'GBA takes over BDA layout maintenance', 'Ordered Jan 2026', 'Pending roads, drains and streetlights now funded 50:50 by BDA and the city corporation; should speed up civic works.', S_GBA)
SETBACKS = P('boost', 'Relaxed setbacks for plots up to 1,500 ft²', 'Notified 2026', 'Small plots get more buildable area, which helps the many small lots in this auction.', S_SETBACK)
PREMIUM_FAR = P('boost', 'Premium FAR / TDR on wider roads', 'Notified 2025-26', 'Plots on roads 9 m+ can buy extra FAR, raising the value of bigger, wider-road sites.', S_FAR)

SOUTH_KNK = [
    P('boost', 'Green Line (Silk Institute terminus, Kanakapura Rd)', 'Operational', 'Metro to Majestic and Yeshwanthpur from the Kanakapura Rd corridor.', S_METRO),
    P('boost', 'Cauvery Stage V water to the southern layouts', 'Main lines laid; house connections pending*', 'Piped water would remove the biggest daily pain (tankers and borewells) in the 6th Stage / Anjanapura belt.', S_WATER),
    GBA_HANDOVER,
]
PROJECTS = {
    'ANJ': SOUTH_KNK + [
        P('concern', 'A decade of slow civic works', 'Ongoing', 'Water and underground drainage still incomplete in parts; resale has lagged neighbours like JP Nagar 9th Phase.', S_WATER),
    ],
    'FEANJ': SOUTH_KNK + [
        P('concern', 'Edge of the city, near the Bannerghatta forest belt*', 'Check', 'Large vacant stretches; eco-sensitive-zone and forest-edge rules may apply to some pockets*. Confirm with BDA.', S_WATER),
    ],
    'BSK6T': SOUTH_KNK[1:] + [
        P('boost', 'Underground drainage for Banashankari 6th Stage', 'Rs 55 cr released; phased*', 'Ends septic-tank dependence; typically lifts resale once streets are connected.', S_UGD),
        P('boost', 'Turahalli tree park protected', 'In place', 'Permanent green buffer next to the 1st and 2nd Blocks.', S_WATER),
    ],
    'BSK6M': SOUTH_KNK[1:] + [
        P('boost', 'Underground drainage for Banashankari 6th Stage', 'Rs 55 cr released; phased*', 'Ends septic-tank dependence once streets are connected.', S_UGD),
        P('boost', 'Kengeri ORR-Ullal and Annapoorneshwari Nagar grade separators', 'Due 2026*', 'Faster access to Mysore Rd and the Purple Line at Kengeri.', S_ROADS),
    ],
    'BSK6N': SOUTH_KNK[1:] + [P('boost', 'Underground drainage for Banashankari 6th Stage', 'Rs 55 cr released; phased*', 'Ends septic-tank dependence once streets are connected.', S_UGD)],
    'BSK6O': SOUTH_KNK[1:] + [
        P('boost', 'Kengeri grade separators', 'Due 2026*', 'Quicker reach to Kengeri metro and Mysore Rd.', S_ROADS),
        P('concern', 'Quarry belt towards Ganakallu', 'Ongoing', 'Blasting dust and heavy trucks on approach roads in some pockets.', S_WATER),
    ],
    'FEBSK': SOUTH_KNK + [
        P('boost', 'Talaghattapura / Kanakapura Rd densifying', 'Ongoing', 'New apartments, schools and retail along Kanakapura Rd raise land demand behind them.', S_METRO),
    ],
    'BTM4': [
        P('boost', 'Pink Line (Kalena Agrahara - Nagawara)', 'Elevated section opening late 2026; underground 2027*', 'Metro along Bannerghatta Rd; IIM-B and JP Nagar 4th Phase stations nearby.', S_METRO),
        PREMIUM_FAR,
    ],
    'BTM6': [
        P('boost', 'Pink Line Hulimavu station', 'Elevated section opening late 2026*', 'Walk-to-metro for parts of BTM 6th Stage.', S_METRO),
        P('concern', 'Hulimavu lake-side flooding', 'Recurring in heavy rain', 'Low-lying streets near the lake have flooded before; check the plot level.', S_METRO),
    ],
    'JPN8': [P('boost', 'Green Line (Konanakunte / Doddakallasandra)', 'Operational', 'Metro within 2-3 km.', S_METRO)],
    'JPN9': [
        P('boost', 'Green Line (Konanakunte / Doddakallasandra)', 'Operational', 'Metro within 2-4 km.', S_METRO),
        P('boost', 'Fast house construction across the layout', 'Ongoing', 'Apartments here rose ~63% in 5 years; plots follow.', S_METRO),
    ],
    'KSL': [P('boost', 'Green Line (Banashankari / Yelachenahalli)', 'Operational', 'Established metro access.', S_METRO), PREMIUM_FAR],
    'SMV': [
        P('boost', 'Purple Line to Challaghatta', 'Operational', 'Kengeri, Jnanabharathi and Challaghatta stations serve the layout.', S_METRO),
        P('boost', 'Kengeri ORR-Ullal grade separator', 'Due 2026*', 'Signal-free run from Ullal to Mysore Rd.', S_ROADS),
        GBA_HANDOVER,
    ],
    'ARKT': [
        P('boost', 'Pink Line terminus at Nagawara', 'Structure ready; opening 2026-27*', 'Metro to Bannerghatta Rd via MG Road.', S_METRO),
        P('boost', 'Blue Line airport metro', 'Hebbal-Airport by Sep 2027*', 'Airport and Hebbal connectivity for the north.', S_METRO),
        P('boost', 'Bengaluru Business Corridor (old PRR), 100 m wide', 'Package 1 awarded 2026; land acquisition partial*', 'Big connectivity boost for Thanisandra-Hennur-Bagalur once built.', S_BBC),
        P('concern', 'Arkavathy "re-do" litigation', 'Pockets unresolved', 'Some allottees were moved to Kempegowda Layout; check the survey number is in the final plan.', S_ARK),
    ],
    'ARKB': [
        P('boost', 'Bengaluru Business Corridor (old PRR), 100 m wide', 'Package 1 awarded; land acquisition partial*', 'Will run near the 18th Block; a major value driver once open.', S_BBC),
        P('concern', 'Corridor alignment overlaps some lots on the RMP map', 'Verify', 'The coarse master-plan map puts several 18th Block lots inside the 100 m corridor. Get written confirmation from BDA.', S_BBC_LAND),
        P('concern', 'Arkavathy "re-do" litigation', 'Pockets unresolved', 'Check the survey number.', S_ARK),
    ],
    'ARKH': [
        P('boost', 'Bengaluru Business Corridor (old PRR)', 'Package 1 awarded*', 'Hennur-Bagalur corridor connectivity.', S_BBC),
        P('boost', 'Blue Line (Kalyan Nagar / HRBR)', 'KR Puram-Hebbal by early 2028*', 'Metro for the Hennur belt.', S_METRO),
        P('concern', 'Arkavathy "re-do" litigation', 'Pockets unresolved', 'Check the survey number.', S_ARK),
    ],
    'ARKJ': [
        P('boost', 'Blue Line airport metro (Jakkur Cross / Kodigehalli)', 'Hebbal-Airport by Sep 2027*', 'Airport corridor metro.', S_METRO),
        P('concern', 'Jakkur aerodrome height limits', 'In force', 'Building height may be capped near the airfield; check before planning G+3.', S_ARK),
        P('concern', 'Arkavathy "re-do" litigation', 'Pockets unresolved', 'Check the survey number.', S_ARK),
    ],
    'ARKS': [
        P('boost', 'Blue Line airport metro', 'Hebbal-Airport by Sep 2027*', 'Jakkur Cross station within reach.', S_METRO),
        P('boost', 'Bengaluru Business Corridor (old PRR)', 'Package 1 awarded*', 'East-west link to Hennur and Old Madras Rd.', S_BBC),
        P('concern', 'Arkavathy "re-do" litigation', 'Pockets unresolved', 'Check the survey number.', S_ARK),
    ],
    'ARKK': [
        P('boost', 'Blue Line (Kalyan Nagar / HRBR)', 'KR Puram-Hebbal by early 2028*', 'Metro for Kalyan Nagar and Kothanur.', S_METRO),
        P('concern', 'Arkavathy "re-do" litigation', 'Pockets unresolved', 'Check the survey number.', S_ARK),
    ],
    'NGEF': [
        P('boost', 'Blue Line (Kasturi Nagar) + Purple Line (Benniganahalli)', 'Purple operational; Blue by 2028*', 'Interchange-level metro access.', S_METRO),
        PREMIUM_FAR,
    ],
}
