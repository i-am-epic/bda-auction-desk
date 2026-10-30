"""Shared city-level reference data, plus the active auction's notice (set AUCTION=<id>, default t15)."""
import importlib.util, os
from market import MARKET  # noqa: F401

AUCTION_ID = os.environ.get('AUCTION', 't15')
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auctions', AUCTION_ID, 'notice.py')
_spec = importlib.util.spec_from_file_location('notice', _p); _n = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_n)
ROWS, WITHDRAWN, LOCALITY, AUCTION = _n.ROWS, _n.WITHDRAWN, _n.LOCALITY, _n.AUCTION

METRO = [  # approx station coords (operational or under construction as of late 2026)
 ('Silk Institute (Green)',12.8619,77.5300),('Doddakallasandra (Green)',12.8846,77.5529),('Konanakunte Cross (Green)',12.8887,77.5627),
 ('Yelachenahalli (Green)',12.8961,77.5701),('Banashankari (Green)',12.9153,77.5735),('Kengeri (Purple)',12.9078,77.4827),
 ('Challaghatta (Purple)',12.8975,77.4617),('Kengeri Bus Terminal (Purple)',12.9145,77.4878),('Pattanagere (Purple)',12.9241,77.4985),
 ('Hulimavu (Pink, u/c)',12.8790,77.6055),('IIM-B (Pink, u/c)',12.8955,77.6012),('JP Nagar 4th Ph (Pink, u/c)',12.9067,77.5920),
 ('Kalena Agrahara (Pink, u/c)',12.8692,77.6022),('Nagawara (Pink, u/c)',13.0420,77.6190),('Hebbal (Blue, u/c)',13.0358,77.5970),
 ('Jakkur Cross (Blue, u/c)',13.0712,77.5987),('Kodigehalli (Blue, u/c)',13.0560,77.5970),('Benniganahalli (Purple)',12.9910,77.6630),
 ('KR Puram (Purple)',13.0007,77.6754),('Swami Vivekananda Rd (Purple)',12.9857,77.6450),('Hosa Road (Yellow)',12.8740,77.6560),
]
HUBS = [('Manyata Tech Park',13.0475,77.6212),('Electronic City',12.8452,77.6600),('Airport (KIA)',13.1989,77.7068),
        ('Silk Board',12.9176,77.6230),('Majestic',12.9767,77.5713),('NICE Rd–Kanakapura Rd jn',12.8790,77.5440)]
