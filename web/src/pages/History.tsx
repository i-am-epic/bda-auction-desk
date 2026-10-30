import { useMemo, useState } from 'react';
import { useHistory } from '../lib/data';
import { fmtDate, rs } from '../lib/format';

const STATUS: Record<string, [string, string]> = {
  FINALIZED: ['Sold / closed', 'accent'], BIDDING_CLOSED: ['Bidding closed', 'accent'], NO_PARTICIPATIONS: ['No bidders', 'bad'],
  NO_BIDS_RECEIVED: ['No bids', 'bad'], CANCELLED: ['Cancelled', ''], UNDER_EVALUATION: ['Under evaluation', 'warn'], EVALUATED: ['Evaluated', 'warn'],
};
const monthName = (m: string) => new Date(`${m}-01`).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });

export default function HistoryPage() {
  const h = useHistory();
  const [tab, setTab] = useState<'rounds' | 'lots'>('rounds');
  const [q, setQ] = useState(''), [loc, setLoc] = useState(''), [st, setSt] = useState(''), [page, setPage] = useState(0);
  const locs = useMemo(() => h ? [...new Set(h.lots.map(l => l.locality).filter(Boolean) as string[])].sort() : [], [h]);
  const lots = useMemo(() => !h ? [] : h.lots.filter(l => (!loc || l.locality === loc) && (!st || (st === 'sold' ? ['FINALIZED', 'BIDDING_CLOSED'].includes(l.status) : st === 'unsold' ? l.status.startsWith('NO_') : l.status === st))
    && (!q || `${l.title} ${l.no}`.toLowerCase().includes(q.toLowerCase()))), [h, q, loc, st]);
  if (!h) return <div className="loading">Loading past auctions…</div>;
  const S = h.summary, PER = 50;
  return (
    <div className="wrap section stack" style={{ gap: 22 }}>
      <div className="section-h" style={{ marginBottom: 0 }}><div><div className="eyebrow">All BDA site auctions on KPPP · {fmtDate(S.first)} to {fmtDate(S.last)}</div>
        <h1 style={{ fontSize: 'clamp(28px,4vw,40px)' }}>Past auctions</h1></div>
        <p>Every BDA lot in the localities we track: when it was auctioned, its base rate, and whether anyone bid. {h.note}</p></div>
      <div className="stats" style={{ marginTop: 0 }}>
        <div><b className="num">{S.lots.toLocaleString('en-IN')}</b><span>lots auctioned</span></div>
        <div><b className="num" style={{ color: 'var(--strong)' }}>{S.sold.toLocaleString('en-IN')}</b><span>sold / closed</span></div>
        <div><b className="num" style={{ color: 'var(--skip)' }}>{S.unsold.toLocaleString('en-IN')}</b><span>no bidders</span></div>
        <div><b className="num">{Math.round(S.sold / (S.sold + S.unsold) * 100)}%</b><span>sell-through</span></div>
        <div><b className="num">{S.relistedSites}</b><span>sites listed 2+ times</span></div>
        <div><b className="num">{h.rounds.length}</b><span>auction months</span></div>
      </div>
      <div className="seg" role="tablist" style={{ alignSelf: 'start' }}>
        <button role="tab" aria-selected={tab === 'rounds'} className={tab === 'rounds' ? 'on' : ''} onClick={() => setTab('rounds')}>By auction round</button>
        <button role="tab" aria-selected={tab === 'lots'} className={tab === 'lots' ? 'on' : ''} onClick={() => setTab('lots')}>Every lot</button>
      </div>
      {tab === 'rounds' ? (
        <div className="stack" style={{ gap: 10 }}>
          {h.rounds.filter(r => r.sold + r.unsold > 0).map(r => {
            const done = r.sold + r.unsold;
            return (
              <details key={r.month} className="card round">
                <summary>
                  <span className="rt"><b>{monthName(r.month)}</b><span className="tiny muted">{fmtDate(r.start)}{r.end !== r.start ? ` – ${fmtDate(r.end)}` : ''}</span></span>
                  <span className="rbar" title={`${r.sold} sold, ${r.unsold} no bidders`}><i style={{ width: `${done ? r.sold / done * 100 : 0}%` }} /></span>
                  <span className="num small">{r.lots} lots · {done ? Math.round(r.sold / done * 100) : 0}% sold</span>
                  <span className="num small muted">{r.medianBase ? `median ${rs(r.medianBase)}/m²` : ''}</span>
                </summary>
                <div className="tbl-wrap" style={{ border: 0, borderTop: '1px solid var(--line)', borderRadius: 0 }}><table className="tbl" style={{ minWidth: 480 }}>
                  <thead><tr><th>Locality</th><th className="n">Sold</th><th className="n">No bidders</th></tr></thead>
                  <tbody>{r.localities.map(([l, s, u]) => <tr key={l}><td>{l}</td><td className="n">{s}</td><td className="n">{u}</td></tr>)}</tbody>
                </table></div>
                <p className="tiny muted" style={{ padding: '8px 14px' }}>Base rates this round: {r.minBase ? `${rs(r.minBase)} to ${rs(r.maxBase)}/m²` : '—'}{r.cancelled ? ` · ${r.cancelled} cancelled` : ''}{r.upcoming ? ` · ${r.upcoming} pending` : ''}</p>
              </details>);
          })}
        </div>
      ) : (
        <div className="stack" style={{ gap: 12 }}>
          <div className="row">
            <input className="field" style={{ flex: '1 1 220px', width: 'auto' }} type="search" placeholder="Search site no., layout or auction no." value={q} onChange={e => { setQ(e.target.value); setPage(0); }} aria-label="Search lots" />
            <select className="field" style={{ flex: '1 1 200px', width: 'auto' }} value={loc} onChange={e => { setLoc(e.target.value); setPage(0); }} aria-label="Locality"><option value="">All localities</option>{locs.map(l => <option key={l}>{l}</option>)}</select>
            <select className="field" style={{ flex: '0 1 160px', width: 'auto' }} value={st} onChange={e => { setSt(e.target.value); setPage(0); }} aria-label="Outcome"><option value="">Any outcome</option><option value="sold">Sold / closed</option><option value="unsold">No bidders</option><option value="CANCELLED">Cancelled</option></select>
          </div>
          <div className="tbl-wrap"><table className="tbl">
            <thead><tr><th>Bid date</th><th>Lot</th><th>Locality</th><th className="n">Base ₹/m²</th><th>Outcome</th></tr></thead>
            <tbody>{lots.slice(page * PER, page * PER + PER).map(l => { const s = STATUS[l.status] ?? [l.status, '']; return (
              <tr key={l.no}><td className="mono small" style={{ whiteSpace: 'nowrap' }}>{fmtDate(l.date)}</td><td>{l.title}<br /><span className="tiny muted">{l.no}</span></td><td className="small">{l.locality ?? '—'}</td>
                <td className="n">{l.base ? l.base.toLocaleString('en-IN') : '—'}</td><td><span className={`pill ${s[1]}`}>{s[0]}</span></td></tr>); })}</tbody>
          </table></div>
          <div className="row"><span className="small muted">{lots.length.toLocaleString('en-IN')} lots</span><span className="spacer" />
            <button className="btn sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
            <span className="small num">{page + 1} / {Math.max(1, Math.ceil(lots.length / PER))}</span>
            <button className="btn sm" disabled={(page + 1) * PER >= lots.length} onClick={() => setPage(page + 1)}>Next</button></div>
        </div>
      )}
    </div>
  );
}
