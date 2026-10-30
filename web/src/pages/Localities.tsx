import { Link, useParams } from 'react-router-dom';
import { useData } from '../lib/data';
import { SiteCard, Sparkline } from '../components/ui';
import { rs } from '../lib/format';

export function Localities() {
  const { meta } = useData();
  if (!meta) return null;
  const groups = Object.values(meta.groups).sort((a, b) => (b.history?.sellThrough ?? 0) - (a.history?.sellThrough ?? 0));
  return (
    <div className="wrap section">
      <div className="section-h"><div><div className="eyebrow">20 areas in this auction</div><h1 style={{ fontSize: 'clamp(28px,4vw,40px)' }}>Localities</h1></div>
        <p>Resale rates, growth outlook and BDA's record from {groups.reduce((a, g) => a + (g.history?.lots ?? 0), 0).toLocaleString('en-IN')} past lots on KPPP. Low sell-through means BDA's base is close to what buyers will pay there.</p></div>
      <div className="tbl-wrap"><table className="tbl">
        <thead><tr><th>Locality</th><th>Growth</th><th className="n">Resale ₹/ft² (low–high)*</th><th className="n">BDA base ₹/ft²</th><th className="n">Past lots</th><th className="n">Sold</th><th>Base-rate trend</th><th className="n">Sites now</th></tr></thead>
        <tbody>{groups.map(g => (
          <tr key={g.id}>
            <td><Link to={`/localities/${g.id}`}><b>{g.name}</b></Link></td>
            <td><span className={`growth-tag g-${g.growth.replace(' ', '-')}`}>{g.growth} ~{g.cagr}%</span></td>
            <td className="n">{g.lo.toLocaleString('en-IN')}–{g.hi.toLocaleString('en-IN')}</td>
            <td className="n">{g.baseRates.map(r => Math.round(r / 10.7639).toLocaleString('en-IN')).join(' / ')}</td>
            <td className="n">{g.history?.lots ?? '—'}</td>
            <td className="n">{g.history ? `${g.history.sellThrough}%` : '—'}</td>
            <td>{g.history && g.history.baseSeries.length > 1 ? <Sparkline series={g.history.baseSeries} w={110} h={26} /> : '—'}</td>
            <td className="n">{g.sites}</td>
          </tr>))}</tbody>
      </table></div>
      <p className="tiny muted" style={{ marginTop: 10 }}>* Realisable resale rate for a regular BDA-khata plot: 2026 asking prices × ~0.85.</p>
    </div>
  );
}

export function LocalityPage() {
  const { id } = useParams();
  const { meta, active } = useData();
  const g = meta && Object.entries(meta.groups).find(([, v]) => v.id === id);
  if (!meta) return null;
  if (!g) return <div className="wrap empty-state"><h3>Locality not found</h3><Link to="/localities">All localities</Link></div>;
  const [key, L] = g;
  const sites = active.filter(s => s.group === key).sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
  return (
    <div className="wrap section stack" style={{ gap: 24 }}>
      <div className="crumbs"><Link to="/localities">Localities</Link>/<span>{L.name}</span></div>
      <div className="section-h" style={{ marginBottom: 0 }}><div><span className={`growth-tag g-${L.growth.replace(' ', '-')}`}>{L.growth} growth · ~{L.cagr}%/yr*</span><h1 style={{ fontSize: 'clamp(28px,4vw,42px)', marginTop: 8 }}>{L.name}</h1></div></div>
      <p className="lede">{L.story}</p>
      <div className="grid3">
        <div className="card pad"><div className="eyebrow">Resale rate*</div><b style={{ fontFamily: 'var(--display)', fontSize: 26 }}>₹{L.lo.toLocaleString('en-IN')}–{L.hi.toLocaleString('en-IN')}/ft²</b><p className="tiny muted">{L.ask}</p></div>
        <div className="card pad"><div className="eyebrow">BDA sell-through</div><b style={{ fontFamily: 'var(--display)', fontSize: 26 }}>{L.history ? `${L.history.sellThrough}% of ${L.history.lots}` : '—'}</b><p className="tiny muted">{L.history ? `${L.history.unsold} past lots drew no bidders.` : 'No past lots found.'}</p></div>
        <div className="card pad"><div className="eyebrow">BDA base-rate trend</div>{L.history && L.history.baseSeries.length > 1 ? <><Sparkline series={L.history.baseSeries} w={260} h={44} /><p className="tiny muted">{L.history.baseSeries.map(([y, v]) => `${y}: ${rs(v)}`).join(' · ')}/m²</p></> : <p className="small muted">{L.history?.baseSeries?.[0] ? `${rs(L.history.baseSeries[0][1])}/m² (${L.history.baseSeries[0][0]})` : '—'}</p>}</div>
      </div>
      <div className="grid2">
        <div className="card pad stack" style={{ gap: 8 }}><b style={{ color: 'var(--strong)' }}>Pushing prices up</b><ul style={{ margin: 0, paddingLeft: 18 }}>{L.drivers.map((d, i) => <li key={i}>{d}</li>)}</ul></div>
        <div className="card pad stack" style={{ gap: 8 }}><b style={{ color: 'var(--skip)' }}>Holding it back</b><ul style={{ margin: 0, paddingLeft: 18 }}>{L.watch.map((d, i) => <li key={i}>{d}</li>)}</ul></div>
      </div>
      <div><div className="eyebrow" style={{ marginBottom: 10 }}>Projects and concerns</div>
        <div className="grid2">{L.projects.map((p, i) => (
          <a key={i} className={`card proj ${p.kind}`} href={p.src} target="_blank" rel="noopener" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="row" style={{ justifyContent: 'space-between' }}><b>{p.name}</b><span className={`pill ${p.kind === 'boost' ? 'accent' : 'bad'}`}>{p.kind === 'boost' ? 'Boost' : 'Concern'}</span></div>
            <span className="st">{p.status}</span><span className="small">{p.effect}</span></a>))}</div></div>
      <div><div className="eyebrow" style={{ marginBottom: 10 }}>{sites.length} sites on sale here</div><div className="picks-grid">{sites.map(s => <SiteCard key={s.id} s={s} />)}</div></div>
    </div>
  );
}
