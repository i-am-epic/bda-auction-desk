import { Link } from 'react-router-dom';
import { useAP, useData } from '../lib/data';
import { shortlist, useShortlist } from '../lib/shortlist';
import { inr, perSqft } from '../lib/format';
import { ScoreRing, Verdict } from '../components/ui';
import type { Site } from '../lib/types';

const ROWS: [string, (s: Site) => React.ReactNode][] = [
  ['Locality', s => s.locality],
  ['Plot', s => `${s.areaSqft.toLocaleString('en-IN')} ft²`],
  ['Minimum bid', s => inr(s.minBidTotal)],
  ['Likely winning bid*', s => `${inr(s.expTotal)} (${perSqft(s.expRate)})`],
  ['Our walk-away*', s => inr(s.maxBidTotal)],
  ['Fair value*', s => inr(s.fairTotal)],
  ['All-in at likely bid*', s => inr(s.allIn)],
  ['Win odds*', s => `${s.winChance}%`],
  ['Competition*', s => s.compLabel],
  ['Area growth*', s => `${s.growth.label} ~${s.growth.cagr}%/yr`],
  ['Rental yield*', s => `${s.rentalYield.toFixed(1)}%`],
  ['Resale return*', s => (s.resaleReturn != null ? `${s.resaleReturn}%/yr` : '—')],
  ['Commercial yield*', s => (s.commercialYield != null ? `${s.commercialYield.toFixed(1)}%` : '—')],
  ['Road width*', s => `~${s.road.ft} ft`],
  ['Facing*', s => s.terrain.facing ?? '—'],
  ['Metro', s => `${s.metro.km} km`],
  ['Auctioned before', s => (s.prevRounds.length ? `${s.prevRounds.length}×` : 'No')],
  ['Red flags', s => [...s.flags, ...s.surroundRisks].filter(f => f.sev === 'bad').length || 'None'],
  ['KPPP number', s => s.kppp?.no ?? '—'],
];

export default function Shortlist() {
  const { byId, aid, meta } = useData();
  const ap = useAP();
  const keys = useShortlist().filter(k => k.startsWith(`${aid}/`));
  const list = keys.map(k => byId.get(k.slice(aid.length + 1))).filter(Boolean) as Site[];
  return (
    <div className="wrap section">
      <div className="section-h"><div><div className="eyebrow">Saved on this device · auction {meta?.auction.code}</div><h1 style={{ fontSize: 'clamp(28px,4vw,40px)' }}>Shortlist &amp; compare</h1></div>
        {list.length > 0 && <button className="btn sm" onClick={() => keys.forEach(k => shortlist.remove(k))}>Clear all</button>}</div>
      {!list.length ? (
        <div className="card empty-state"><h3>Nothing shortlisted yet</h3><p>Tap the star on any site to save it here and compare side by side.</p><p style={{ marginTop: 14 }}><Link className="btn primary" to={ap('/explore')}>Explore sites</Link></p></div>
      ) : (
        <div className="tbl-wrap"><table className="tbl cmp">
          <thead><tr><th>Site</th>{list.map(s => (
            <th key={s.id} style={{ minWidth: 180, textTransform: 'none', letterSpacing: 0 }}>
              <div className="row" style={{ gap: 8 }}><ScoreRing site={s} size={38} /><div><Link to={ap(`/site/${s.id}`)} style={{ fontSize: 15, fontFamily: 'var(--display)', color: 'var(--ink)' }}>Site {s.site}</Link><br /><Verdict s={s} /></div></div>
              <button className="btn sm ghost" style={{ marginTop: 6 }} onClick={() => shortlist.remove(`${aid}/${s.id}`)}>Remove</button>
            </th>))}</tr></thead>
          <tbody>{ROWS.map(([l, f]) => <tr key={l}><td>{l}</td>{list.map(s => <td key={s.id}>{f(s)}</td>)}</tr>)}</tbody>
        </table></div>
      )}
      <p className="tiny muted" style={{ marginTop: 10 }}>* estimate or model output.</p>
    </div>
  );
}
