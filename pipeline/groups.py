"""Classify KPPP lot titles into the locality groups used in market.py."""
import re

norm = lambda t: re.sub(r'[^0-9A-Z]', '', str(t).upper())

# ---------- classify a KPPP title into our locality groups ----------
def group_of(title):
    t = ' ' + re.sub(r'[^A-Z0-9 ]', ' ', title.upper()) + ' '
    fe = bool(re.search(r' F E | FE | FURTHER ', t))
    if 'ANJANAPURA' in t: return 'FEANJ' if fe else 'ANJ'
    # result tables often drop the stage ("Banashankari 9th Block"); every BDA Banashankari block in these auctions is 6th Stage
    if 'BANASHANKARI' in t and ('6' in t or re.search(r' \d+(ST|ND|RD|TH) BLOCK', t)):
        if fe: return 'FEBSK'
        if 'TURAHALLI' in t or re.search(r' (1ST|2ND) BLOCK', t): return 'BSK6T'
        if ' 9TH BLOCK' in t: return 'BSK6N'
        if re.search(r'SOMPURA|GANAKAL|GANKAL|11TH BLOCK|10TH BLOCK|7TH BLOCK', t): return 'BSK6O'
        return 'BSK6M'
    if 'ARKAVATH' in t:
        for k, g in (('THANISANDRA', 'ARKT'), ('RACHENAHALLI', 'ARKT'), ('BYRATHI', 'ARKB'), ('BYARATHI', 'ARKB'), ('HENNUR', 'ARKH'),
                     ('JAKKUR', 'ARKJ'), ('SRIRAMPURA', 'ARKJ'), ('SAMPIGEHALLI', 'ARKS'), ('VENKATESHAPURA', 'ARKS'),
                     ('NARAYANAPURA', 'ARKK'), ('CHALLAKERE', 'ARKK'), ('CHELLAKERE', 'ARKK')):
            if k in t: return g
        # no village named: map by block number (Arkavathy block -> village belt)
        m = re.search(r' (\d+)(ST|ND|RD|TH)( & \d+TH)? BLOCK', t)
        blk = {'1': 'ARKJ', '2': 'ARKS', '3': 'ARKS', '7': 'ARKJ', '8': 'ARKS', '10': 'ARKH', '11': 'ARKT', '15': 'ARKT',
               '16': 'ARKH', '18': 'ARKB', '19': 'ARKK', '20': 'ARKT', '5': 'ARKK'}
        return blk.get(m.group(1)) if m else None
    if 'VISHWESHWARAIAH' in t or 'VISVESVARAYA' in t or 'VISHVESHWARAH' in t: return 'SMV'
    if 'NPKL' in t or 'KEMPEGOWDA' in t: return 'NPKL'
    if 'NAGAR' in t and re.search(r'J ?P NAGAR', t):
        return 'JPN8' if '8TH' in t else 'JPN9' if '9TH' in t else None
    if 'KUMARASWAMY' in t: return 'KSL'
    if 'BTM' in t: return 'BTM4' if '4TH' in t else 'BTM6' if '6' in t else None
    if 'NGEF' in t: return 'NGEF'
    return None

def site_of(title):
    m = re.search(r'SITE\s*NO\.?\s*-?\s*([0-9A-Z/\-]+)', title.upper().replace(' -', '-'))
    return norm(m.group(1)) if m else None

