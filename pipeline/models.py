"""Two models learned from BDA's own outcomes, replacing hand-set rules.

1. Winning-price model (regression). Data: real final bids from closed BDA auctions (fetch_results.py).
   Target: log(final / base). Features: log plot area, small-plot flag, log(market rate / base) i.e. how cheap BDA's base is,
   and locality (ridge-shrunk towards the overall mean). Gives a predictive distribution, so we can quote a P10-P90 range
   and the chance that a given bid wins.
2. Sell-odds model (classification). Data: every closed BDA lot on KPPP (sold vs no bidders).
   Features: locality, log(market rate / base), year, times listed before, unsold before, odd site number (suffix like 255/L),
   lots of the same locality in the same round. Validated on a time split: trained on lots before 2026, tested on 2026.

Usage: python models.py inputs/bid_results.json build/<id>/kppp_history.json build/<id>/data.json build/<id>/models.json"""
import json, math, os, re, sys
from collections import defaultdict
import numpy as np
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score, brier_score_loss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from market import MARKET
from groups import group_of, site_of

res_p, hist_p, data_p, out_p = sys.argv[1:5]
SQFT = 10.7639
NPKL_MID = 7000   # Rs/ft2, Kempegowda Layout (NPKL) resale estimate; NPKL is only used as training data
mid_sqm = lambda g: (MARKET[g]['mid'] if g in MARKET else NPKL_MID if g == 'NPKL' else None)
GROUPS = sorted(set(MARKET) | {'NPKL'})

def onehot(g):
    return [1.0 if g == x else 0.0 for x in GROUPS]

now_t = 2026 + 10 / 12
# ---------------------------------------------------------------- 2. sell odds
SOLD, UNSOLD = {'FINALIZED', 'BIDDING_CLOSED'}, {'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED'}
hist = json.load(open(hist_p, encoding='utf8'))
lots = []
for h in hist:
    if h['statusKey'] not in SOLD | UNSOLD or not h.get('bidDate') or not h.get('baseRate'): continue
    g = group_of(h['auctionTitle'])
    if g not in MARKET: continue
    d = h['bidDate']; t = int(d[6:10]) + (int(d[3:5]) - 1) / 12
    lots.append(dict(g=g, site=site_of(h['auctionTitle']), t=t, base=h['baseRate'], sold=h['statusKey'] in SOLD, month=d[6:10] + d[3:5]))
lots.sort(key=lambda l: l['t'])
seen = defaultdict(list); supply = defaultdict(int)
for l in lots: supply[(l['g'], l['month'])] += 1
for l in lots:
    prev = seen[(l['g'], l['site'])]
    l['nprev'] = len(prev); l['unsold_before'] = any(not p for p in prev)
    seen[(l['g'], l['site'])].append(l['sold'])

sold_rate = defaultdict(lambda: [0, 0])
for l in lots: sold_rate[l['g']][0] += l['sold']; sold_rate[l['g']][1] += 1
overall = sum(v[0] for v in sold_rate.values()) / max(1, sum(v[1] for v in sold_rate.values()))
demand = lambda g: (sold_rate[g][0] + 5*overall) / (sold_rate[g][1] + 5) if g in sold_rate else overall   # shrunk sell-through

# ---------------------------------------------------------------- 1. winning price
bids = [b for b in json.load(open(res_p, encoding='utf8')) if b['group']]
def prem_x(area, base, g):
    m = mid_sqm(g)
    attract = math.log(m * SQFT / base) if m else 0.0
    return [math.log(area), 1.0 if area < 100 else 0.0, attract, demand(g)] + onehot(g)
X = np.array([prem_x(b['area'], b['base'], b['group']) for b in bids])
y = np.array([math.log(b['final'] / b['base']) for b in bids])

def cv_ridge(alpha, k=5):
    errs, res = [], np.zeros(len(y))
    for tr, te in KFold(k, shuffle=True, random_state=7).split(X):
        m = Ridge(alpha=alpha).fit(X[tr], y[tr]); p = m.predict(X[te])
        res[te] = y[te] - p
        errs += list(np.abs(np.exp(y[te]) - np.exp(p)))   # error in "final / base" units, i.e. premium points
    return float(np.mean(errs)), res
best = min(((a,) + cv_ridge(a) for a in (0.1, 0.3, 1, 3, 10, 30)), key=lambda t: t[1])
alpha, mae, resid = best
prem_model = Ridge(alpha=alpha).fit(X, y)
sigma = float(np.std(resid))
q10, q90 = (float(np.quantile(resid, q)) for q in (0.1, 0.9))
# baselines for comparison: global median premium, and the old rule (+10..65% by competition, ~+27% median)
base_glob = float(np.mean(np.abs(np.exp(y) - np.median(np.exp(y)))))
base_rule = float(np.mean(np.abs(np.exp(y) - 1.27)))
coef = dict(zip(['log_area', 'small_plot', 'cheapness', 'locality_demand'], [round(float(c), 3) for c in prem_model.coef_[:4]]))
print(f'premium model: n={len(y)} alpha={alpha} CV MAE={mae*100:.0f} pts (global median {base_glob*100:.0f}, old rule {base_rule*100:.0f}) sigma={sigma:.2f}')
print('  coefs', coef)

comps = defaultdict(list)
for b in bids: comps[b['group']].append(b['final'] / SQFT)
comps = {g: dict(n=len(v), medianSqft=round(float(np.median(v))), p25=round(float(np.quantile(v, .25))), p75=round(float(np.quantile(v, .75))))
         for g, v in comps.items()}

def sell_x(g, base, t, nprev, unsold_before, site, sup):
    m = mid_sqm(g)
    return [math.log(m * SQFT / base), min(nprev, 4), 1.0 if unsold_before else 0.0,
            1.0 if re.search(r'[A-Z/]', site or '') else 0.0, math.log(1 + sup)] + onehot(g)
SX = np.array([sell_x(l['g'], l['base'], l['t'], l['nprev'], l['unsold_before'], l['site'], supply[(l['g'], l['month'])]) for l in lots])
SY = np.array([1 if l['sold'] else 0 for l in lots])
split = np.array([l['t'] < 2026 for l in lots])
W = np.array([0.5 ** ((2026 - l['t']) / 1.0) for l in lots])
clf = LogisticRegression(C=1.0, max_iter=2000).fit(SX[split], SY[split], sample_weight=W[split])
p_te = clf.predict_proba(SX[~split])[:, 1]
auc = float(roc_auc_score(SY[~split], p_te)); brier = float(brier_score_loss(SY[~split], p_te))
brier_base = float(brier_score_loss(SY[~split], np.full((~split).sum(), SY[split].mean())))
print(f'sell model: train {split.sum()} (pre-2026), test {(~split).sum()} (2026): AUC={auc:.2f} Brier={brier:.3f} (base-rate Brier {brier_base:.3f})')
clf = LogisticRegression(C=1.0, max_iter=2000).fit(SX, SY, sample_weight=0.5 ** ((now_t - np.array([l['t'] for l in lots])) / 1.0))   # refit on everything, recent lots weighted up
scoef = dict(zip(['cheapness', 'times_listed', 'unsold_before', 'odd_site_no', 'round_supply'], [round(float(c), 3) for c in clf.coef_[0][:5]]))
print('  coefs', scoef)

# ---------------------------------------------------------------- score the current auction
sites = json.load(open(data_p, encoding='utf8'))
now = 2026 + 10 / 12
cur_sup = defaultdict(int)
for s in sites:
    if s['status'] == 'active': cur_sup[s['group']] += 1
past = defaultdict(list)
for l in lots: past[(l['g'], l['site'])].append(l['sold'])
norm = lambda t: re.sub(r'[^0-9A-Z]', '', str(t).upper())
scores = {}
for s in sites:
    g = s['group']
    prev = past.get((g, norm(s['site'])), [])
    px = np.array([prem_x(s.get('area_corr') or s['area'], s['rate'], g)])
    mu = float(prem_model.predict(px)[0])
    sx = np.array([sell_x(g, s['rate'], now, len(prev), any(not p for p in prev), norm(s['site']), cur_sup[g])])
    scores[s['sl'] + '|' + s['site']] = dict(pSell=round(float(clf.predict_proba(sx)[0, 1]), 3), mu=round(mu, 4),
                                             lo=round(mu + q10, 4), hi=round(mu + q90, 4))
json.dump(dict(
    premium=dict(n=len(y), alpha=alpha, cvMaePts=round(mae * 100), baselineGlobalPts=round(base_glob * 100), baselineOldRulePts=round(base_rule * 100),
                 sigma=round(sigma, 3), q10=round(q10, 3), q90=round(q90, 3), coef=coef, medianPremium=round(float(np.median(np.exp(y)) - 1) * 100),
                 auctions=sorted({b['auction'] for b in bids})),
    sell=dict(nTrain=int(split.sum()), nTest=int((~split).sum()), auc=round(auc, 3), brier=round(brier, 4), brierBase=round(brier_base, 4),
              n=len(SY), soldRate=round(float(SY.mean()), 3), coef=scoef),
    comps=comps, sites=scores), open(out_p, 'w', encoding='utf8'), indent=1)
print('scored', len(scores))
