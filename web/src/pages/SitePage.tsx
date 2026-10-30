import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useData } from '../lib/data';
import type { Site } from '../lib/types';
import { fmtDate, inr, kpppDate, perSqft, rs, SQFT } from '../lib/format';
import { commercialOk } from '../lib/filters';
import { Est, Icon, Meter, ScoreRing, SiteCard, SiteTags, StarButton, Verdict, useToast } from '../components/ui';
import { MiniMap } from '../components/MapView';

const SECTIONS = [['summary', 'Summary'], ['price', 'Price & bid'], ['history', 'History'], ['location', 'Location & risks'],
  ['returns', 'Returns'], ['buyers', 'Buyer views'], ['plot', 'Plot data']] as const;
const SEV: Record<string, string> = { bad: 'RISK', warn: 'CHECK', info: 'NOTE', good: 'GOOD', neutral: 'NOTE', ok: 'OK' };
const STATUS: Record<string, [string, string]> = {
  FINALIZED: ['Closed with a result', 's'], BIDDING_CLOSED: ['Bidding closed', 's'], NO_PARTICIPATIONS: ['No bidders', 'u'],
  NO_BIDS_RECEIVED: ['No bids', 'u'], CANCELLED: ['Cancelled', ''],
};
const NEAR_LABEL: Record<string, string> = { lake: 'Lake / tank', drain: 'Stormwater drain', canal: 'Canal / river', htline: 'High-tension line', majorroad: 'Arterial road',
  midroad: 'Collector road', rail: 'Railway', cemetery: 'Burial ground', stp: 'Sewage plant', garbage: 'Waste site', industrial: 'Industrial land',
  quarry: 'Quarry', green: 'Park / forest', school: 'School / college', hospital: 'Hospital / clinic', shop: 'Shops', bus: 'Bus stop' };

function useActiveSection() {
  const [on, setOn] = useState('summary');
  useEffect(() => {
    const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && setOn(e.target.id)), { rootMargin: '-40% 0px -55% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  });
  return on;
}

function Flags({ items }: { items: { sev: string; text: string }[] }) {
  if (!items.length) return null;
  return <ul className="flags">{items.map((f, i) => <li key={i} className={f.sev}><span className="k">{SEV[f.sev]}</span><span>{f.text}</span></li>)}</ul>;
}

function BidBar({ s }: { s: Site }) {
  const lo = s.rate * 0.95, hi = Math.max(s.fairHi, s.expHi / (s.area_corr ?? s.area), s.maxBidRate) * 1.05;
  const x = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`;
  const billed = s.area_corr ?? s.area;
  return (
    <div className="card pad">
      <div className="bidbar" aria-hidden="true">
        <div className="axis" />
        <div className="zone" style={{ left: x(s.expLo / billed), width: `calc(${x(s.expHi / billed)} - ${x(s.expLo / billed)})` }} />
        <div className="mk" style={{ left: x(s.minBidRate) }}>Min bid<i /></div>
        <div className="mk" style={{ left: x(s.expRate) }}><b>Likely</b><i /></div>
        <div className="mk b" style={{ left: x(s.maxBidRate) }}><i />Walk away</div>
        <div className="mk b" style={{ left: x(s.fairRate) }}><i />Fair</div>
      </div>
      <p className="small muted" style={{ marginTop: 18 }}>Amber band: the likely winning range ({inr(s.expLo)} – {inr(s.expHi)}). Expected winner pays about <b>{s.expPremium}% over base</b>, scaled by competition and calibrated to BDA's Dec 2021 results (+62% average).<Est /></p>
    </div>
  );
}

function RentCalc({ s }: { s: Site }) {
  const c = s.commercial!;
  const [rent, setRent] = useState(c.rent);
  const cost = s.allIn + c.build;
  return (
    <div className="card calc">
      <div className="row"><b>Commercial rent calculator</b><span className="pill accent">On a {c.road}</span></div>
      <p className="small muted">About {c.gfSqft} ft² of ground-floor shop{c.upperSqft ? ` plus ${c.upperSqft} ft² upstairs` : ''} after setbacks<Est how="GBA 2026 small-plot setbacks: 0.75 m front, 0.6 m one side; shops need 1.8 m depth" />. Drag to the rent you think the spot can earn.</p>
      <label className="small" htmlFor="rent">Monthly rent: <b className="num">{rs(rent)}</b></label>
      <input id="rent" type="range" min={2000} max={Math.max(60000, c.rent * 3)} step={500} value={rent} onChange={e => setRent(Number(e.target.value))} />
      <div className="out">
        <div><small>Total outlay</small><b className="num">{inr(cost)}</b></div>
        <div><small>Gross yield</small><b className="num">{((rent * 12) / cost * 100).toFixed(1)}%</b></div>
        <div><small>Payback</small><b className="num">{(cost / (rent * 12)).toFixed(0)} yrs</b></div>
      </div>
      <p className="tiny muted">Needs commercial use permitted for this BDA site (zoning on wide roads plus BDA/GBA approval) and a trade licence. Model rent: {rs(c.rent)}/month at ~₹{c.rate}/ft² ground floor.<Est /></p>
    </div>
  );
}

export default function SitePage() {
  const { id } = useParams();
  const { byId, active, meta, loading } = useData();
  const s = id ? byId.get(id) : undefined;
  const on = useActiveSection();
  const [toast, show] = useToast();
  const similar = useMemo(() => s ? active.filter(x => x.group === s.group && x.id !== s.id).sort((a, b) => (b.score ?? 0) - (a.score ?? 0)).slice(0, 3) : [], [s, active]);
  useEffect(() => { if (s) document.title = `Site ${s.site}, ${s.locality} · BDA Auction Desk`; return () => { document.title = 'BDA Auction Desk'; }; }, [s]);
  if (loading) return null;
  if (!s || !meta) return <div className="wrap empty-state"><h3>Site not found</h3><p><Link to="/explore">Back to all sites</Link></p></div>;

  const billed = s.area_corr ?? s.area;
  const copy = () => { navigator.clipboard?.writeText(s.kppp!.no).then(() => show(`Copied ${s.kppp!.no}`), () => show('Select the number and copy it')); };
  const risks = [...s.surroundRisks];
  const nearRows = Object.entries(s.near).filter(([k]) => NEAR_LABEL[k]).sort((a, b) => a[1].m - b[1].m).slice(0, 12);
  const boosts = s.projects.filter(p => p.kind === 'boost'), concerns = s.projects.filter(p => p.kind === 'concern');

  return (
    <>
      <div className="site-hero">
        <div className="wrap">
          <div className="crumbs"><Link to="/explore">Explore</Link>/<Link to={`/localities/${s.group.toLowerCase()}`}>{s.locality}</Link>/<span>Site {s.site}</span></div>
          <div className="site-head">
            <ScoreRing site={s} size={72} />
            <div style={{ minWidth: 0 }}>
              <div className="row"><Verdict s={s} /><SiteTags s={s} max={5} /></div>
              <h1>Site {s.site}</h1>
              <div className="sub">{s.layout} · Sl {s.sl} · {s.zone} zone{s.bidDay ? ` · bids ${fmtDate(s.bidDay)}` : ''}</div>
            </div>
            <div className="site-actions">
              <StarButton id={s.id} />
              <a className="btn" href={`https://www.google.com/maps?q=${s.lat},${s.lon}`} target="_blank" rel="noopener">Google Maps <Icon name="ext" size={14} /></a>
              {s.kppp && <button className="btn primary" onClick={copy}><Icon name="copy" size={15} />Copy KPPP no.</button>}
            </div>
          </div>
          <div className="keyfigs">
            <div><small>Plot</small><b className="num">{s.areaSqft.toLocaleString('en-IN')} ft²</b><em>{s.area} m²</em></div>
            <div><small>Minimum valid bid</small><b className="num">{inr(s.minBidTotal)}</b><em>{perSqft(s.minBidRate)}</em></div>
            <div><small>Likely winning bid<Est /></small><b className="num">{inr(s.expTotal)}</b><em>{perSqft(s.expRate)}</em></div>
            <div><small>Fair value<Est /></small><b className="num">{inr(s.fairTotal)}</b><em>{perSqft(s.fairRate)}</em></div>
            <div><small>Win odds at walk-away<Est /></small><b className="num">{s.winChance}%</b><em>{s.compLabel.toLowerCase()} competition</em></div>
          </div>
        </div>
        <nav className="subnav" aria-label="Sections"><div className="wrap">
          {SECTIONS.map(([k, l]) => <a key={k} href={`#${k}`} className={on === k ? 'on' : ''} onClick={e => { e.preventDefault(); document.getElementById(k)?.scrollIntoView({ behavior: 'smooth' }); }}>{l}</a>)}
        </div></nav>
      </div>

      <div className="wrap site-body">
        <div>
          <section className="blk" id="summary">
            <h2>Summary</h2>
            <p className="lede">{s.description}</p>
            {s.findings.length > 0 && <div className="card pad"><div className="eyebrow" style={{ marginBottom: 10 }}>What stands out</div><ul className="find-list">{s.findings.map((f, i) => <li key={i}>{f}</li>)}</ul></div>}
            <div className="grid2">
              <div className="card pad stack" style={{ gap: 8 }}><b style={{ color: 'var(--strong)' }}>Why buy</b><ul style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 6, fontSize: 14 }}>{s.pros.map((p, i) => <li key={i}>{p}</li>)}</ul></div>
              <div className="card pad stack" style={{ gap: 8 }}><b style={{ color: 'var(--skip)' }}>Why not</b><ul style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 6, fontSize: 14 }}>{s.cons.slice(0, 6).map((p, i) => <li key={i}>{p}</li>)}</ul></div>
            </div>
            <Flags items={s.flags} />
          </section>

          <section className="blk" id="price">
            <h2>Price &amp; bid <small>per ft² unless noted</small></h2>
            <BidBar s={s} />
            <div className="card pad"><div className="ladder">
              {([['BDA base', s.rate, 'var(--off)'], ['Minimum bid (+10%)', s.minBidRate, 'var(--ink-3)'], ['Likely winning bid*', s.expRate, 'var(--fair)'],
                 ['Our walk-away*', s.maxBidRate, 'var(--accent)'], ['Fair value*', s.fairRate, 'var(--strong)']] as [string, number, string][]).map(([l, v, c]) => {
                const mx = Math.max(s.fairHi, s.expRate, s.maxBidRate) * 1.05;
                return <div className="rung" key={l}><span>{l}</span><span className="track"><span className="fill" style={{ width: `${v / mx * 100}%`, background: c }} />
                  {l.startsWith('Fair') && <span className="rng" style={{ left: `${s.fairLo / mx * 100}%`, width: `${(s.fairHi - s.fairLo) / mx * 100}%` }} />}</span><span className="v">{rs(v / SQFT)}</span></div>;
              })}
            </div>
            <p className="small muted" style={{ marginTop: 12 }}>Area evidence: {s.growth.ask}. Valued on {s.valueBasis}.{s.usability < 1 ? ` Discounted ${Math.round((1 - s.usability) * 100)}% for size or shape.` : ''}{s.marketCap?.applied ? ' Capped by an earlier price at which nobody bid.' : ''}</p></div>
            <div className="grid2">
              <div className="card pad"><table className="kv"><tbody>
                <tr><td>Base price ({billed} m²)</td><td>{inr(s.baseTotal)}</td></tr>
                <tr><td>Likely winning bid<Est /></td><td>{inr(s.expTotal)}</td></tr>
                <tr><td>Stamp duty + registration (~6.6%)</td><td>{inr(s.stampReg)}</td></tr>
                <tr><td>Khata, legal, misc.</td><td>{inr(50000)}</td></tr>
                <tr className="tot"><td>All-in</td><td>{inr(s.allIn)}</td></tr>
                {s.tds > 0 && <tr><td>1% TDS you deduct and remit</td><td>{inr(s.tds)}</td></tr>}
              </tbody></table></div>
              <div className="card pad"><table className="kv"><tbody>
                <tr><td>EMD now (refundable)</td><td>{inr(meta.auction.emd)}</td></tr>
                <tr><td>Within 72 h of advice letter</td><td>{inr(Math.max(0, s.expTotal * 0.25 - meta.auction.emd))}</td></tr>
                <tr><td>Within 45 days of allotment</td><td>{inr(s.expTotal * 0.75)}</td></tr>
                <tr><td>Expected bidders<Est /></td><td>{s.bidders}</td></tr>
                <tr><td>Chance nobody else bids<Est /></td><td>{s.noBidRisk}%</td></tr>
              </tbody></table><p className="tiny muted" style={{ marginTop: 8 }}>A lone bidder is rejected by BDA; the site returns in a later round.</p></div>
            </div>
          </section>

          <section className="blk" id="history">
            <h2>Bidding history <small>from KPPP</small></h2>
            <div className="card pad">
              {s.prevRounds.length ? (
                <ul className="tl">
                  {s.prevRounds.map((p, i) => { const st = STATUS[p.status] ?? [p.status, '']; return (
                    <li key={i} className={st[1]}><span className="dot" /><span className="mono small">{kpppDate(p.date)}</span><span>{st[0]} <span className="tiny muted">· {p.no}</span></span><span className="mono small">{p.base ? `${rs(p.base)}/m²` : ''}</span></li>); })}
                  <li className="now"><span className="dot" /><span className="mono small">2–4 Nov 2026</span><span><b>This auction</b></span><span className="mono small">{rs(s.rate)}/m²</span></li>
                </ul>) : <p className="muted">First time on auction: no earlier rounds for this exact site.</p>}
              <p className="small muted" style={{ marginTop: 12 }}>KPPP does not publish winning amounts. "Closed with a result" followed by a re-listing usually means a single bidder (rejected) or a winner who did not pay.</p>
            </div>
          </section>

          <section className="blk" id="location">
            <h2>Location &amp; risks</h2>
            <MiniMap s={s} />
            {s.geotag === 'approx' && <p className="small muted">This site is not on BDA's geotag map. The dashed outline is drawn from the notice dimensions near the closest mapped sites in the block.<Est /></p>}
            <Flags items={[...risks, ...s.surroundGoods.map(t => ({ sev: 'good', text: t })), ...s.vastu.map(v => ({ sev: v.kind === 'bad' ? 'warn' : v.kind, text: v.text }))]} />
            <div className="grid2">
              <div className="card pad"><div className="eyebrow" style={{ marginBottom: 8 }}>Distances (OpenStreetMap)</div><table className="kv"><tbody>
                <tr><td>Metro: {s.metro.name}</td><td>{s.metro.km} km</td></tr>
                {s.hubs.map(h => <tr key={h.name}><td>{h.name}</td><td>{h.km} km</td></tr>)}
                {nearRows.map(([k, v]) => <tr key={k}><td>{NEAR_LABEL[k]}{v.name ? ` · ${v.name}` : ''}</td><td>{v.m >= 1000 ? `${(v.m / 1000).toFixed(1)} km` : `${v.m} m`}</td></tr>)}
              </tbody></table></div>
              <div className="card pad"><div className="eyebrow" style={{ marginBottom: 8 }}>Road &amp; land</div><table className="kv"><tbody>
                <tr><td>Road width today{s.road.conf !== 'Mapped' && <Est how={s.road.source} />}</td><td>{s.road.range ? `${s.road.range[0]}–${s.road.range[1]}` : s.road.width} m · ~{s.road.ft} ft</td></tr>
                <tr className="sub"><td colSpan={2}>{s.road.source}</td></tr>
                {s.road.planned && <tr><td>Planned width (RMP map)</td><td>{s.road.planned.width} m</td></tr>}
                <tr><td>FAR from road width<Est /></td><td>{s.far}</td></tr>
                <tr><td>Facing (nearest road side)<Est /></td><td>{s.terrain.facing ?? 'Unclear'}</td></tr>
                <tr><td>Elevation (SRTM 30 m)<Est /></td><td>{s.terrain.elev ?? '—'} m</td></tr>
                <tr><td>Ground falls towards<Est /></td><td>{s.terrain.aspect ?? '—'}{s.terrain.slope != null ? ` · ${s.terrain.slope}%` : ''}</td></tr>
              </tbody></table></div>
            </div>
            <div className="eyebrow">Coming up nearby</div>
            <div className="grid2">
              {[...boosts, ...concerns].map((p, i) => (
                <a key={i} className={`card proj ${p.kind}`} href={p.src} target="_blank" rel="noopener" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div className="row" style={{ justifyContent: 'space-between' }}><b style={{ fontSize: 14.5 }}>{p.name}</b><span className={`pill ${p.kind === 'boost' ? 'accent' : 'bad'}`}>{p.kind === 'boost' ? 'Boost' : 'Concern'}</span></div>
                  <span className="st">{p.status}</span><span className="small">{p.effect}</span>
                </a>))}
            </div>
            <div className="grid2">
              <div className="card pad stack" style={{ gap: 6 }}><b>Area growth: {s.growth.label} (~{s.growth.cagr}%/yr)<Est /></b><p className="small">{s.growth.story}</p></div>
              <div className="card pad stack" style={{ gap: 6 }}><b>Holding it back</b><ul style={{ margin: 0, paddingLeft: 18, fontSize: 14 }}>{s.growth.watch.map((w, i) => <li key={i}>{w}</li>)}</ul></div>
            </div>
          </section>

          <section className="blk" id="returns">
            <h2>Returns <small>all estimates*</small></h2>
            <div className="grid3">
              <div className="card pad"><div className="eyebrow">Rental yield</div><b style={{ fontFamily: 'var(--display)', fontSize: 30 }}>{s.rentalYield.toFixed(1)}%</b><p className="small muted">Build {s.floors}, {s.builtUpSqft.toLocaleString('en-IN')} ft² at FAR {s.far}; rent {inr(s.rentMonthly)}/mo on {inr(s.projectCost)} total.</p></div>
              <div className="card pad"><div className="eyebrow">Resale return</div><b style={{ fontFamily: 'var(--display)', fontSize: 30 }}>{s.resaleReturn != null ? `${s.resaleReturn}%/yr` : '—'}</b><p className="small muted">Worth about {inr(s.value5y)} in 5 years ({s.gain5y > 0 ? '+' : ''}{s.gain5y}% on {inr(s.allIn)} all-in).</p></div>
              <div className="card pad"><div className="eyebrow">Commercial yield</div><b style={{ fontFamily: 'var(--display)', fontSize: 30 }}>{s.commercialYield != null ? `${s.commercialYield.toFixed(1)}%` : '—'}</b><p className="small muted">{commercialOk(s) ? `Shop/office on a ${s.commercial!.road}.` : s.commercial ? 'Wide road, but too shallow for a usable shop.' : 'Not on a wide road; residential use assumed.'}</p></div>
            </div>
            {commercialOk(s) && <RentCalc s={s} />}
          </section>

          <section className="blk" id="buyers">
            <h2>How different buyers will see it</h2>
            <div className="grid2">
              {s.personas.map(p => (
                <div key={p.who} className="card persona-c">
                  <span className={`pill ${p.fit === 'Good fit' ? 'accent' : p.fit === 'Possible' ? 'warn' : 'bad'} fit`}>{p.fit}</span>
                  <b>{p.who}</b><p className="small">{p.think}</p>
                </div>))}
            </div>
          </section>

          <section className="blk" id="plot">
            <h2>Plot data</h2>
            <div className="card pad"><table className="kv"><tbody>
              <tr><td>Dimensions (E–W × N–S)</td><td>{s.ew} × {s.ns} m</td></tr>
              <tr><td>Area</td><td>{s.area} m² · {s.areaSqft.toLocaleString('en-IN')} ft²</td></tr>
              {s.area_corr && <tr><td>Area per corrigendum</td><td>{s.area_corr} m²</td></tr>}
              {s.polyArea && <tr><td>BDA map outline measures</td><td>{s.polyArea} m²</td></tr>}
              <tr><td>BDA base rate</td><td>{rs(s.rate)}/m² · {rs(s.ratePerSqft)}/ft²</td></tr>
              <tr><td>Source</td><td>{s.source}</td></tr>
              <tr><td>Coordinates</td><td>{s.lat.toFixed(5)}, {s.lon.toFixed(5)}</td></tr>
            </tbody></table></div>
          </section>
        </div>

        <aside className="side">
          <div className="card apply">
            <div className="eyebrow">Apply on KPPP</div>
            {s.kppp ? <>
              <code>{s.kppp.no}</code>
              <span className="tiny muted">{s.kppp.title}</span>
              <div className="row"><button className="btn primary sm" onClick={copy}><Icon name="copy" size={14} />Copy number</button><a className="btn sm" href={meta.auction.kppp} target="_blank" rel="noopener">Open KPPP <Icon name="ext" size={13} /></a></div>
              <span className="tiny muted">Log in, open Auctions, set status to "Published" and paste this number. KPPP has no direct link for a single lot.</span>
            </> : <span className="small">Not yet listed on KPPP. Search KPPP for "Site No-{s.site}".</span>}
          </div>
          {s.scoreParts && <div className="card pad stack" style={{ gap: 10 }}>
            <div className="eyebrow">Rating breakdown</div>
            <Meter label="Value after likely bid" value={s.scoreParts.value} />
            <Meter label="Area growth" value={s.scoreParts.growth} />
            <Meter label="Location" value={s.scoreParts.location} />
            <Meter label="Usability" value={s.scoreParts.usability} />
            <Meter label="Data & surroundings" value={s.scoreParts.confidence} />
            <Meter label="Odds of winning" value={s.scoreParts.odds} />
            <p className="tiny muted">Missing data is estimated, never scored as a negative.</p>
          </div>}
          {similar.length > 0 && <div className="stack" style={{ gap: 10 }}><div className="eyebrow">Others in {s.locality}</div>{similar.map(x => <SiteCard key={x.id} s={x} />)}</div>}
        </aside>
      </div>
      {toast}
    </>
  );
}
