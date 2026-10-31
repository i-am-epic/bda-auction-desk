import { useEffect, useState } from 'react';
import { useCurrentAuctionId } from '../lib/data';
import type { Meta } from '../lib/types';

export default function Method() {
  const aid = useCurrentAuctionId();
  const [meta, setMeta] = useState<Meta | null>(null);
  useEffect(() => { if (aid) fetch(`/data/${aid}/meta.json`).then(r => r.json()).then(setMeta).catch(() => {}); }, [aid]);
  const M = meta?.models;
  return (
    <div className="wrap section">
      <div className="prose">
        <div className="eyebrow">How it works</div>
        <h1 style={{ fontSize: 'clamp(28px,4vw,40px)' }}>Method &amp; sources</h1>
        <p>Every figure marked <sup className="est">*</sup> is an estimate or model output. Everything else is read directly from BDA, KPPP or a map. Where data is missing we estimate it; missing data never lowers a rating.</p>
        <h2>1. Validity</h2>
        <p>Each site in BDA notice {meta?.auction.notice} is matched to BDA's geotag map (121 polygons). We flag withdrawn, duplicated and "Not found" sites, area/dimension mismatches, and wedges narrower than 3 m. Sites missing from BDA's map get an outline drawn from the notice dimensions next to the closest mapped sites in the same block.</p>
        <h2>2. Fair value</h2>
        <p>Each locality has a 2026 realisable rate for a regular BDA-khata plot (asking prices × ~0.85, from 99acres, NoBroker, BDAsites, 360plot, TalkingLands, Nestoria). It is discounted for small, narrow or irregular plots and adjusted for facing and road width. If nobody bid on this exact site at an earlier base, fair value is capped at that base + 10%, grown at the area rate. For small plots on wide roads we also value the land on shop rent (6.5% gross yield, minus 25% for commercial-permission risk) and use the higher figure.</p>
        <h2 id="models">3. Two models learned from BDA's own results</h2>
        <p><b>Winning price.</b> A ridge regression trained on {M ? M.premium.n : 'about 200'} real final bids from closed BDA auctions ({M?.premium.auctions.join(', ') ?? 'T-08, T-11'}). Those are the only per-lot winning prices we found, archived by bdaeauction.in; KPPP itself doesn't publish winning amounts. It predicts the winning price as a premium over base, from plot size, how cheap BDA's base is against the area's market rate, how often lots in the locality sell, and the locality itself. Winners paid a median <b>{M ? `+${M.premium.medianPremium}%` : '+93%'}</b> over base. In cross-validation its predictions are typically within <b>±{M?.premium.cvMaePts ?? 53} points</b> of the real premium. A single average would miss by ±{M?.premium.baselineGlobalPts ?? 55}, and our earlier rule (+27% median) by ±{M?.premium.baselineOldRulePts ?? 81}. Each site shows a range covering 80% of outcomes, not one number.</p>
        <p><b>Chance it sells.</b> A logistic regression trained on {M ? M.sell.n.toLocaleString('en-IN') : '2,590'} closed BDA lots on KPPP, labelled sold or no bidders. Recent lots count more. The strongest signals are how cheap the base is against the market (cheaper sells far more often) and whether the site went unsold before (it often does again). Odd site numbers like 255/L, and many similar lots in the same round, also lower the odds. Trained only on lots before 2026 and tested on {M ? M.sell.nTest.toLocaleString('en-IN') : '1,176'} lots from 2026 that it never saw, it ranks lots well (AUC {M?.sell.auc ?? 0.7}; 0.5 is a coin toss). Its probabilities are also more accurate than assuming the average sell rate (Brier score {M?.sell.brier ?? 0.198} against {M?.sell.brierBase ?? 0.223}; lower is better).</p>
        <p><b>Fair value</b> now also blends in these real auction prices for the locality, with more weight where there are more results.</p>
        <p><b>Real bid sheets.</b> For sites in the current auction that were auctioned before, we collect the actual bidding from a signed-in KPPP account, de-identified (bidder count and amounts only, no names). Across 64 of them, 73% of results were rejected, 45% drew a single bidder, and the winning premium rose from about +10% with one bidder to +196% with ten or more — bidder count is the strongest price driver. A real result overrides the model for that site.</p>
        <p className="small muted">Limits: the price data is small and noisy, and half of it comes from Kempegowda Layout, so treat each predicted premium as a range. The models retrain on every pipeline run, so they improve as BDA publishes more results.</p>
        <h2>4. Competition and win odds</h2>
        <p>Competition blends the sell model with locality demand. It is adjusted for BDA's sell-through in that locality across 2,742 past KPPP lots, ticket size, plot usability, whether this exact site drew no bidders before, and whether it was re-listed after closing. Win odds are the chance our walk-away bid (95% of fair value) beats every expected rival.</p>
        <h2>5. Surroundings, terrain and roads</h2>
        <p>Lakes, drains, power lines, roads, rail, burial grounds, sewage plants, quarries, parks, schools and bus stops come from OpenStreetMap (31,000+ features). Elevation and slope come from SRTM 30 m, which is coarse for one plot. Road width comes from an OSM width tag where mapped. Otherwise it is estimated from the BBMP/RMP road-width map (planned widths), the OSM road class and BDA layout norms. Road width sets FAR: 1.75 under 12 m, 2.25 for 12–18 m, 2.5 for 18 m and above.</p>
        <h2>6. Rating</h2>
        <p>30% value after the likely bid, 15% area growth, 15% location, 15% usability, 15% data and surroundings confidence, 10% win odds. Any serious red flag (drain or lake edge within metres, HT line, withdrawn, "Not found") caps the rating at 5.</p>
        <h2>Sources</h2>
        <ul>
          <li><a href={meta?.auction.notice_pdf} target="_blank" rel="noopener">BDA e-auction notification T-15</a> and <a href={meta?.auction.corrigendum_pdf} target="_blank" rel="noopener">corrigendum 1574</a></li>
          <li>BDA geotag map; <a href="https://kppp.karnataka.gov.in/" target="_blank" rel="noopener">KPPP</a> lot listings and history</li>
          <li><a href="https://data.opencity.in/dataset/bengaluru-road-width-map" target="_blank" rel="noopener">BBMP road width map (OpenCity)</a>, OpenStreetMap, SRTM via OpenTopoData</li>
          <li>Context: GBA layout handover, BSK 6th Stage UGD, Bengaluru Business Corridor, Namma Metro timelines, GBA 2026 setback relaxation. Each project card links to its source.</li>
        </ul>
        <p className="small muted">This site is decision support, not a valuation or legal opinion. Confirm every figure with BDA, a registered valuer and a property lawyer before bidding.</p>
      </div>
    </div>
  );
}
