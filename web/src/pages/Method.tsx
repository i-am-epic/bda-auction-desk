import { useData } from '../lib/data';

export default function Method() {
  const { meta } = useData();
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
        <h2>3. Likely winning bid</h2>
        <p>KPPP does not publish winning amounts, so we calibrate to BDA's reported results: in December 2021, 296 sites sold for about ₹348 cr against about ₹215 cr expected (+62%), with corner sites at +44% (<a href={meta?.calibration.src} target="_blank" rel="noopener">source</a>). The expected premium over base runs from +10% at very low competition to +65% at very high competition, capped at the top of the resale range.</p>
        <h2>4. Competition and win odds</h2>
        <p>Competition starts from locality demand. It is adjusted for BDA's sell-through in that locality across 2,742 past KPPP lots, ticket size, plot usability, whether this exact site drew no bidders before, and whether it was re-listed after closing. Win odds are the chance our walk-away bid (95% of fair value) beats every expected rival.</p>
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
