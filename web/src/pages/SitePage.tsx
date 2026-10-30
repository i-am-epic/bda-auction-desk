import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useAP, useData } from '../lib/data';
import type { Site } from '../lib/types';
import { fmtDate, inr, kpppDate, perSqft, rs, SQFT } from '../lib/format';
import { commercialOk } from '../lib/filters';
import { Est, Icon, Meter, ScoreRing, SiteCard, SiteTags, StarButton, Verdict, useToast } from '../components/ui';
import { MiniMap } from '../components/MapView';

const TABS = [['overview', 'Overview'], ['price', 'Price & bid'], ['history', 'Bid history'], ['area', 'Area & risks'],
  ['location', 'Map & land'], ['returns', 'Returns'], ['buyers', 'Buyer views'], ['data', 'Plot data']] as const;
type Tab = typeof TABS[number][0];
const SEV: Record<string, string> = { bad: 'RISK', warn: 'CHECK', info: 'NOTE', good: 'GOOD', neutral: 'NOTE', ok: 'OK' };
const STATUS: Record<string, [string, string]> = {
  FINALIZED: ['Closed with a result', 's'], BIDDING_CLOSED: ['Bidding closed', 's'], NO_PARTICIPATIONS: ['No bidders', 'u'],
  NO_BIDS_RECEIVED: ['No bids', 'u'], CANCELLED: ['Cancelled', ''],
};
const NEAR_LABEL: Record<string, string> = { lake: 'Lake / tank', drain: 'Stormwater drain', canal: 'Canal / river', htline: 'High-tension line', majorroad: 'Arterial road',
  midroad: 'Collector road', rail: 'Railway', cemetery: 'Burial ground', stp: 'Sewage plant', garbage: 'Waste site', industrial: 'Industrial land',
  quarry: 'Quarry', green: 'Park / forest', school: 'School / college', hospital: 'Hospital / clinic', shop: 'Shops', bus: 'Bus stop' };

function Flags({ items }: { items: { sev: string; text: string }[] }) {
  if (!items.length) return null;
  return <ul className="flags">{items.map((f, i) => <li key={i} className={f.sev}><span className="k">{SEV[f.sev]}</span><span>{f.text}</span></li>)}</ul>;
}
/** Shows the first n items and a "Show all" toggle for the rest, so long lists don't swamp the page. */
function More<T>({ items, n, render }: { items: T[]; n: number; render: (x: T, i: number) => ReactNode }) {
  const [all, setAll] = useState(false);
  return <>{(all ? items : items.slice(0, n)).map(render)}{items.length > n && <li style={{ listStyle: 'none' }}><button className="linkbtn" onClick={() => setAll(!all)}>{all ? 'Show less' : `Show all ${items.length}`}</button></li>}</>;
}

function BidBar({ s }: { s: Site }) {
  const billed = s.area_corr ?? s.area;
  const lo = s.rate * 0.95, hi = Math.max(s.fairHi, s.expHi / billed, s.maxBidRate) * 1.05;
  const x = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`;
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
      <p className="small muted" style={{ marginTop: 18 }}>Amber band: the likely winning range, {inr(s.expLo)} to {inr(s.expHi)}. The expected winner pays about <b>{s.expPremium}% over base</b>, scaled by competition and calibrated to BDA's Dec 2021 results (+62% average).<Est /></p>
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
      <p className="tiny muted">Needs commercial use permitted for this BDA site and a trade licence. Model rent: {rs(c.rent)}/month at about ₹{c.rate}/ft² for the ground floor.<Est /></p>
    </div>
  );
}

export default function SitePage() {
  const { id } = useParams();
  const { byId, active, meta } = useData();
  const ap = useAP();
  const [params, setParams] = useSearchParams();
  const tab = (TABS.find(t => t[0] === params.get('tab'))?.[0] ?? 'overview') as Tab;
  const setTab = (t: Tab) => setParams(t === 'overview' ? {} : { tab: t }, { replace: true });
  const s = id ? byId.get(id) : undefined;
  const [toast, show] = useToast();
  const similar = useMemo(() => s ? active.filter(x => x.group === s.group && x.id !== s.id).sort((a, b) => (b.score ?? 0) - (a.score ?? 0)).slice(0, 3) : [], [s, active]);
  useEffect(() => { if (s && meta) document.title = `Site ${s.site}, ${s.locality} · ${meta.auction.code} · BDA Auction Desk`; return () => { document.title = 'BDA Auction Desk'; }; }, [s, meta]);
  if (!s || !meta) return <div className="wrap empty-state"><h3>Site not found in this auction</h3><p><Link to={ap('/explore')}>Back to all sites</Link></p></div>;

  const billed = s.area_corr ?? s.area;
  const copy = () => { navigator.clipboard?.writeText(s.kppp!.no).then(() => show(`Copied ${s.kppp!.no}`), () => show('Select the number and copy it')); };
  const nearRows = Object.entries(s.near).filter(([k]) => NEAR_LABEL[k]).sort((a, b) => a[1].m - b[1].m);
  const reds = [...s.flags, ...s.surroundRisks].filter(f => f.sev === 'bad');
  const checks = [...s.flags, ...s.surroundRisks].filter(f => f.sev !== 'bad');

  return (
    <>
      <div className="site-hero">
        <div className="wrap">
          <div className="crumbs"><Link to={ap('/explore')}>{meta.auction.code} sites</Link>/<Link to={ap(`/localities/${s.group.toLowerCase()}`)}>{s.locality}</Link>/<span>Site {s.site}</span></div>
          <div className="site-head">
            <ScoreRing site={s} size={72} />
            <div style={{ minWidth: 0 }}>
              <div className="row"><Verdict s={s} /><SiteTags s={s} max={4} /></div>
              <h1>Site {s.site}</h1>
              <div className="sub">{s.layout} · Sl {s.sl}{s.bidDay ? ` · bidding ${fmtDate(s.bidDay)}` : ''}</div>
            </div>
            <div className="site-actions">
              <StarButton id={s.id} />
              <a className="btn" href={`https://www.google.com/maps?q=${s.lat},${s.lon}`} target="_blank" rel="noopener">Google Maps <Icon name="ext" size={14} /></a>
              {s.kppp && <button className="btn primary" onClick={copy}><Icon name="copy" size={15} />{s.kppp.no.replace('BDA/2026-27/', '')}</button>}
            </div>
          </div>
          <div className="keyfigs">
            <div><small>Plot</small><b className="num">{s.areaSqft.toLocaleString('en-IN')} ft²</b><em>{s.area} m²</em></div>
            <div><small>Minimum valid bid</small><b className="num">{inr(s.minBidTotal)}</b><em>{perSqft(s.minBidRate)}</em></div>
            <div><small>Likely winning bid<Est /></small><b className="num">{inr(s.expTotal)}</b><em>{s.expPremium}% over base</em></div>
            <div><small>Fair value<Est /></small><b className="num">{inr(s.fairTotal)}</b><em>{perSqft(s.fairRate)}</em></div>
            <div><small>Win odds at walk-away<Est /></small><b className="num">{s.winChance}%</b><em>{s.compLabel.toLowerCase()} competition</em></div>
          </div>
        </div>
        <nav className="subnav" aria-label="Report sections"><div className="wrap" role="tablist">
          {TABS.map(([k, l]) => <button key={k} role="tab" aria-selected={tab === k} className={tab === k ? 'on' : ''} onClick={() => setTab(k)}>{l}
            {k === 'area' && reds.length > 0 && <span className="dotc bad">{reds.length}</span>}{k === 'history' && s.prevRounds.length > 0 && <span className="dotc">{s.prevRounds.length}</span>}</button>)}
        </div></nav>
      </div>

      <div className="wrap tabbody">
        {tab === 'overview' && (
          <div className="ov">
            <div className="stack">
              <p className="lede">{s.description}</p>
              <div className="grid2">
                <div className="card pad stack" style={{ gap: 8 }}><b style={{ color: 'var(--strong)' }}>Why buy</b><ul className="plain"><More items={s.pros} n={3} render={(p, i) => <li key={i}>{p}</li>} /></ul></div>
                <div className="card pad stack" style={{ gap: 8 }}><b style={{ color: 'var(--skip)' }}>Why not</b><ul className="plain"><More items={s.cons} n={3} render={(p, i) => <li key={i}>{p}</li>} /></ul></div>
              </div>
              {s.findings.length > 0 && <div className="card pad"><div className="eyebrow" style={{ marginBottom: 10 }}>What stands out</div><ul className="find-list"><More items={s.findings} n={3} render={(f, i) => <li key={i}>{f}</li>} /></ul></div>}
              {reds.length > 0 && <div><div className="eyebrow" style={{ marginBottom: 8 }}>Red flags</div><Flags items={reds} /></div>}
              {similar.length > 0 && <div><div className="eyebrow" style={{ marginBottom: 10 }}>Others in {s.locality}</div><div className="picks-grid">{similar.map(x => <SiteCard key={x.id} s={x} />)}</div></div>}
            </div>
            <aside className="stack">
              <div className="card apply">
                <div className="eyebrow">Apply on KPPP</div>
                {s.kppp ? <>
                  <code>{s.kppp.no}</code>
                  <span className="tiny muted">{s.kppp.title}</span>
                  <div className="row"><button className="btn primary sm" onClick={copy}><Icon name="copy" size={14} />Copy number</button><a className="btn sm" href={meta.auction.kppp} target="_blank" rel="noopener">Open KPPP <Icon name="ext" size={13} /></a></div>
                  <span className="tiny muted">Log in, open Auctions, set the status to "Published" and paste this number. KPPP has no direct link for a single lot.</span>
                </> : <span className="small">Not on KPPP yet. Search KPPP for "Site No-{s.site}".</span>}
              </div>
              {s.scoreParts && <div className="card pad stack" style={{ gap: 10 }}>
                <div className="eyebrow">Why it scores {s.score}</div>
                <Meter label="Value after likely bid" value={s.scoreParts.value} />
                <Meter label="Area growth" value={s.scoreParts.growth} />
                <Meter label="Location" value={s.scoreParts.location} />
                <Meter label="Usability" value={s.scoreParts.usability} />
                <Meter label="Data & surroundings" value={s.scoreParts.confidence} />
                <Meter label="Odds of winning" value={s.scoreParts.odds} />
              </div>}
            </aside>
          </div>
        )}

        {tab === 'price' && (
          <div className="stack">
            <BidBar s={s} />
            <div className="card pad"><div className="ladder">
              {([['BDA base', s.rate, 'var(--off)'], ['Minimum bid (+10%)', s.minBidRate, 'var(--ink-3)'], ['Likely winning bid*', s.expRate, 'var(--fair)'],
                ['Our walk-away*', s.maxBidRate, 'var(--accent)'], ['Fair value*', s.fairRate, 'var(--strong)']] as [string, number, string][]).map(([l, v, c]) => {
                const mx = Math.max(s.fairHi, s.expRate, s.maxBidRate) * 1.05;
                return <div className="rung" key={l}><span>{l}</span><span className="track"><span className="fill" style={{ width: `${v / mx * 100}%`, background: c }} />
                  {l.startsWith('Fair') && <span className="rng" style={{ left: `${s.fairLo / mx * 100}%`, width: `${(s.fairHi - s.fairLo) / mx * 100}%` }} />}</span><span className="v">{rs(v / SQFT)}/ft²</span></div>;
              })}
            </div>
            <p className="small muted" style={{ marginTop: 12 }}>Evidence for this area: {s.growth.ask}. Valued on {s.valueBasis}.{s.usability < 1 ? ` Discounted ${Math.round((1 - s.usability) * 100)}% for size or shape.` : ''}{s.marketCap?.applied ? ' Capped by an earlier price at which nobody bid.' : ''}</p></div>
            <div className="grid2">
              <div className="card pad"><div className="eyebrow" style={{ marginBottom: 6 }}>What you pay</div><table className="kv"><tbody>
                <tr><td>Base price ({billed} m²)</td><td>{inr(s.baseTotal)}</td></tr>
                <tr><td>Likely winning bid<Est /></td><td>{inr(s.expTotal)}</td></tr>
                <tr><td>Stamp duty + registration (~6.6%)</td><td>{inr(s.stampReg)}</td></tr>
                <tr><td>Khata, legal, misc.</td><td>{inr(50000)}</td></tr>
                <tr className="tot"><td>All-in</td><td>{inr(s.allIn)}</td></tr>
                {s.tds > 0 && <tr><td>1% TDS you deduct and remit</td><td>{inr(s.tds)}</td></tr>}
              </tbody></table></div>
              <div className="card pad"><div className="eyebrow" style={{ marginBottom: 6 }}>When you pay</div><table className="kv"><tbody>
                <tr><td>EMD before bidding (refundable)</td><td>{inr(meta.auction.emd)}</td></tr>
                <tr><td>Within 72 h of advice letter</td><td>{inr(Math.max(0, s.expTotal * 0.25 - meta.auction.emd))}</td></tr>
                <tr><td>Within 45 days of allotment</td><td>{inr(s.expTotal * 0.75)}</td></tr>
                <tr><td>Expected bidders<Est /></td><td>{s.bidders}</td></tr>
                <tr><td>Chance nobody else bids<Est /></td><td>{s.noBidRisk}%</td></tr>
              </tbody></table><p className="tiny muted" style={{ marginTop: 8 }}>BDA rejects a lone bidder, and the site returns in a later round.</p></div>
            </div>
          </div>
        )}

        {tab === 'history' && (
          <div className="stack">
            <div className="card pad">
              {s.prevRounds.length ? (
                <ul className="tl">
                  {s.prevRounds.map((p, i) => { const st = STATUS[p.status] ?? [p.status, '']; return (
                    <li key={i} className={st[1]}><span className="dot" /><span className="mono small">{kpppDate(p.date)}</span><span>{st[0]} <span className="tiny muted">· {p.no}</span></span><span className="mono small">{p.base ? `${rs(p.base)}/m²` : ''}</span></li>); })}
                  <li className="now"><span className="dot" /><span className="mono small">{meta.auction.bidDays.map(d => fmtDate(d.date).replace(/ 20\d\d$/, '')).join(' – ')}</span><span><b>This auction ({meta.auction.code})</b></span><span className="mono small">{rs(s.rate)}/m²</span></li>
                </ul>) : <p className="muted">First time on auction: no earlier rounds for this exact site on KPPP.</p>}
            </div>
            <div className="card pad small muted">KPPP shows each round's outcome and base rate, but not the winning amount. "Closed with a result" followed by a re-listing usually means a single bidder (rejected) or a winner who didn't pay. <Link to="/history">See every past BDA auction</Link>.</div>
          </div>
        )}

        {tab === 'area' && (
          <div className="stack">
            <div className="grid2">
              <div className="card pad stack" style={{ gap: 6 }}><b>{s.locality}: {s.growth.label} growth (~{s.growth.cagr}%/yr)<Est /></b><p className="small">{s.growth.story}</p></div>
              <div className="card pad stack" style={{ gap: 6 }}><b>Holding it back</b><ul className="plain small">{s.growth.watch.map((w, i) => <li key={i}>{w}</li>)}</ul></div>
            </div>
            <div><div className="eyebrow" style={{ marginBottom: 8 }}>Around this plot (OpenStreetMap)</div>
              <Flags items={[...reds, ...checks, ...s.surroundGoods.map(t => ({ sev: 'good', text: t }))]} /></div>
            <div><div className="eyebrow" style={{ marginBottom: 8 }}>Coming up nearby</div>
              <div className="grid2">{s.projects.map((p, i) => (
                <a key={i} className={`card proj ${p.kind}`} href={p.src} target="_blank" rel="noopener" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div className="row" style={{ justifyContent: 'space-between' }}><b style={{ fontSize: 14.5 }}>{p.name}</b><span className={`pill ${p.kind === 'boost' ? 'accent' : 'bad'}`}>{p.kind === 'boost' ? 'Boost' : 'Concern'}</span></div>
                  <span className="st">{p.status}</span><span className="small">{p.effect}</span></a>))}</div></div>
          </div>
        )}

        {tab === 'location' && (
          <div className="stack">
            <MiniMap s={s} others={active} />
            <p className="small muted">{s.geotag === 'official' ? `Outline from BDA's official geotag map (${s.polyArea} m² as drawn).` : <>{s.geoNote}<Est /></>}</p>
            <div className="grid2">
              <div className="card pad"><div className="eyebrow" style={{ marginBottom: 8 }}>Road &amp; land</div><table className="kv"><tbody>
                <tr><td>Road width today{s.road.conf !== 'Mapped' && <Est how={s.road.source} />}</td><td>{s.road.range ? `${s.road.range[0]}–${s.road.range[1]}` : s.road.width} m · ~{s.road.ft} ft</td></tr>
                <tr className="sub"><td colSpan={2}>{s.road.source}</td></tr>
                {s.road.planned && <tr><td>Planned width (RMP map)</td><td>{s.road.planned.width} m</td></tr>}
                <tr><td>FAR from road width<Est /></td><td>{s.far}</td></tr>
                <tr><td>Facing (nearest road side)<Est /></td><td>{s.terrain.facing ?? 'Unclear'}</td></tr>
                <tr><td>Elevation (SRTM 30 m)<Est /></td><td>{s.terrain.elev ?? '—'} m</td></tr>
                <tr><td>Ground falls towards<Est /></td><td>{s.terrain.aspect ?? '—'}{s.terrain.slope != null ? ` · ${s.terrain.slope}%` : ''}</td></tr>
              </tbody></table>{s.vastu.length > 0 && <div style={{ marginTop: 10 }}><Flags items={s.vastu.map(v => ({ sev: v.kind === 'bad' ? 'warn' : v.kind, text: v.text }))} /></div>}</div>
              <div className="card pad"><div className="eyebrow" style={{ marginBottom: 8 }}>Distances</div><table className="kv"><tbody>
                <tr><td>Metro: {s.metro.name}</td><td>{s.metro.km} km</td></tr>
                {s.hubs.map(h => <tr key={h.name}><td>{h.name}</td><td>{h.km} km</td></tr>)}
                {nearRows.slice(0, 10).map(([k, v]) => <tr key={k}><td>{NEAR_LABEL[k]}{v.name ? ` · ${v.name}` : ''}</td><td>{v.m >= 1000 ? `${(v.m / 1000).toFixed(1)} km` : `${v.m} m`}</td></tr>)}
              </tbody></table></div>
            </div>
          </div>
        )}

        {tab === 'returns' && (
          <div className="stack">
            <div className="grid3">
              <div className="card pad"><div className="eyebrow">Rental yield<Est /></div><b className="bigfig">{s.rentalYield.toFixed(1)}%</b><p className="small muted">Build {s.floors}, {s.builtUpSqft.toLocaleString('en-IN')} ft² at FAR {s.far}; rent {inr(s.rentMonthly)}/mo on {inr(s.projectCost)} total.</p></div>
              <div className="card pad"><div className="eyebrow">Resale return<Est /></div><b className="bigfig">{s.resaleReturn != null ? `${s.resaleReturn}%/yr` : '—'}</b><p className="small muted">Worth about {inr(s.value5y)} in 5 years ({s.gain5y > 0 ? '+' : ''}{s.gain5y}% on {inr(s.allIn)} all-in).</p></div>
              <div className="card pad"><div className="eyebrow">Commercial yield<Est /></div><b className="bigfig">{s.commercialYield != null ? `${s.commercialYield.toFixed(1)}%` : '—'}</b><p className="small muted">{commercialOk(s) ? `Shop or office on a ${s.commercial!.road}.` : s.commercial ? 'On a wide road, but too shallow for a usable shop.' : 'Not on a wide road; residential use assumed.'}</p></div>
            </div>
            {commercialOk(s) && <RentCalc s={s} />}
            <div className="card pad"><table className="kv"><tbody>
              <tr><td>Likely use</td><td style={{ fontFamily: 'var(--body)' }}>{s.use}</td></tr>
              <tr><td>Built-up potential</td><td>{s.builtUpSqft.toLocaleString('en-IN')} ft² · {s.floors}</td></tr>
              <tr><td>Construction at ~₹2,600/ft²<Est /></td><td>{inr(s.buildCost)}</td></tr>
            </tbody></table></div>
          </div>
        )}

        {tab === 'buyers' && (
          <div className="grid2">
            {s.personas.map(p => (
              <div key={p.who} className="card persona-c">
                <span className={`pill ${p.fit === 'Good fit' ? 'accent' : p.fit === 'Possible' ? 'warn' : 'bad'} fit`}>{p.fit}</span>
                <b>{p.who}</b><p className="small">{p.think}</p>
              </div>))}
          </div>
        )}

        {tab === 'data' && (
          <div className="grid2">
            <div className="card pad"><table className="kv"><tbody>
              <tr><td>Auction</td><td>{meta.auction.code}</td></tr>
              <tr><td>Serial no. in notice</td><td>{s.sl}</td></tr>
              <tr><td>Dimensions (E–W × N–S)</td><td>{s.ew} × {s.ns} m</td></tr>
              <tr><td>Area</td><td>{s.area} m² · {s.areaSqft.toLocaleString('en-IN')} ft²</td></tr>
              {s.area_corr && <tr><td>Area per corrigendum</td><td>{s.area_corr} m²</td></tr>}
              {s.polyArea && <tr><td>BDA map outline measures</td><td>{s.polyArea} m²</td></tr>}
              <tr><td>BDA base rate</td><td>{rs(s.rate)}/m² · {rs(s.ratePerSqft)}/ft²</td></tr>
              <tr><td>Source</td><td>{s.source}</td></tr>
              <tr><td>Location basis</td><td>{s.geotag === 'official' ? 'BDA geotag' : s.placement === 'pin' ? 'Per-site pin*' : s.placement === 'adjacent' ? 'Beside block neighbour*' : 'Locality point*'}</td></tr>
              <tr><td>Coordinates</td><td>{s.lat.toFixed(5)}, {s.lon.toFixed(5)}</td></tr>
            </tbody></table></div>
            <div className="card pad"><div className="eyebrow" style={{ marginBottom: 8 }}>Data checks</div><Flags items={checks.length ? checks : [{ sev: 'ok', text: 'No data issues found' }]} /></div>
          </div>
        )}
      </div>
      {toast}
    </>
  );
}
