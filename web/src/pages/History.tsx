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
  const [tab, setTab] = useState<'rounds' | 'lots' | 'why'>('rounds');
  const [q, setQ] = useState(''), [loc, setLoc] = useState(''), [st, setSt] = useState(''), [page, setPage] = useState(0);
  const locs = useMemo(() => h ? [...new Set(h.lots.map(l => l.locality).filter(Boolean) as string[])].sort() : [], [h]);
  const lots = useMemo(() => !h ? [] : h.lots.filter(l => (!loc || l.locality === loc) && (!st || (st === 'sold' ? ['FINALIZED', 'BIDDING_CLOSED'].includes(l.status) : st === 'unsold' ? l.status.startsWith('NO_') : st === 'final' ? !!l.final : l.status === st))
    && (!q || `${l.title} ${l.no}`.toLowerCase().includes(q.toLowerCase()))), [h, q, loc, st]);
  if (!h) return <div className="loading">Loading past auctions…</div>;
  const S = h.summary, PER = 50;
  return (
    <div className="wrap section stack" style={{ gap: 22 }}>
      <div className="section-h" style={{ marginBottom: 0 }}><div><div className="eyebrow">All BDA site auctions on KPPP · {fmtDate(S.first)} to {fmtDate(S.last)}</div>
        <h1 style={{ fontSize: 'clamp(28px,4vw,40px)' }}>Past auctions</h1></div>
        <p>Every BDA lot in the localities we track: when it was auctioned, its base rate, whether anyone bid, and why lots were cancelled. {h.note}</p></div>
      <div className="row">
        <a className="btn sm" href="/data/downloads/bda_kppp_lot_history.csv" download>Download all {S.lots.toLocaleString('en-IN')} lots (CSV)</a>
        <a className="btn sm" href="/data/downloads/bda_real_final_bids.csv" download>Download real final bids (CSV)</a>
        <span className="tiny muted">{h.finalsKnown} of these lots have a known final bid.</span>
      </div>
      <div className="stats" style={{ marginTop: 0 }}>
        <div><b className="num">{S.lots.toLocaleString('en-IN')}</b><span>lots auctioned</span></div>
        <div><b className="num" style={{ color: 'var(--strong)' }}>{S.sold.toLocaleString('en-IN')}</b><span>sold / closed</span></div>
        <div><b className="num" style={{ color: 'var(--skip)' }}>{S.unsold.toLocaleString('en-IN')}</b><span>no bidders</span></div>
        <div><b className="num">{Math.round(S.sold / (S.sold + S.unsold) * 100)}%</b><span>sell-through</span></div>
        <div><b className="num">{S.relistedSites}</b><span>sites listed 2+ times</span></div>
        <div><b className="num">{h.rounds.length}</b><span>auction months</span></div>
      </div>
      {h.realBidStats && <div className="card pad realbid" style={{ borderColor: 'var(--gold)' }}>
        <div className="eyebrow">What real bidding reveals</div>
        <div className="insights" style={{ gap: 12 }}>
          <div><b style={{ fontFamily: 'var(--display)', fontSize: 30, color: 'var(--skip)' }}>{h.realBidStats.rejectedPct}%</b><p className="small muted">of {h.realBidStats.sites} real past results for this auction's sites were <b>rejected</b> — single bidder, below reserve, or the winner never paid.</p></div>
          <div><b style={{ fontFamily: 'var(--display)', fontSize: 30 }}>{h.realBidStats.oneBidderPct}%</b><p className="small muted">drew just <b>one bidder</b> (median {h.realBidStats.medianBidders}). BDA rejects single bidders, so these can't sell.</p></div>
          <div><b style={{ fontFamily: 'var(--display)', fontSize: 30 }}>+{h.realBidStats.premOne}% → +{h.realBidStats.premMany}%</b><p className="small muted">what the winner pays over base goes from about +{h.realBidStats.premOne}% with one bidder to +{h.realBidStats.premMany}% with 10+ bidders. <b>Bidder count is the price driver.</b></p></div>
        </div>
        <p className="tiny muted">{h.realBidStats.note}</p>
      </div>}
      <div className="seg" role="tablist" style={{ alignSelf: 'start' }}>
        <button role="tab" aria-selected={tab === 'rounds'} className={tab === 'rounds' ? 'on' : ''} onClick={() => setTab('rounds')}>By auction round</button>
        <button role="tab" aria-selected={tab === 'lots'} className={tab === 'lots' ? 'on' : ''} onClick={() => setTab('lots')}>Every lot</button>
        <button role="tab" aria-selected={tab === 'why'} className={tab === 'why' ? 'on' : ''} onClick={() => setTab('why')}>Why cancelled</button>
      </div>
      {tab === 'why' && (
        <div className="stack" style={{ gap: 10 }}>
          <p className="small muted">BDA records a reason whenever it pulls a lot from an auction. Court cases and forest or lake buffers are the ones to check against any site you bid on.</p>
          {h.cancellations.map(([cat, list]) => (
            <details key={cat} className="card round" open={/Court|Forest/.test(cat)}>
              <summary><span className="rt"><b>{cat}</b><span className="tiny muted">{list.length} lot{list.length === 1 ? '' : 's'}</span></span>
                <span className={`pill ${/Court|Forest/.test(cat) ? 'bad' : ''}`}>{/Court|Forest/.test(cat) ? 'Legal / environmental' : 'Administrative'}</span><span /><span /></summary>
              <div className="tbl-wrap" style={{ border: 0, borderTop: '1px solid var(--line)', borderRadius: 0 }}><table className="tbl" style={{ minWidth: 560 }}>
                <thead><tr><th>Bid date</th><th>Lot</th><th>Reason given by BDA</th></tr></thead>
                <tbody>{list.map(x => <tr key={x.no}><td className="mono small" style={{ whiteSpace: 'nowrap' }}>{fmtDate(x.date)}</td><td>{x.title}<br /><span className="tiny muted">{x.no}{x.locality ? ` · ${x.locality}` : ''}</span></td><td className="small">{x.reason ?? '—'}</td></tr>)}</tbody>
              </table></div>
            </details>))}
        </div>
      )}
      {tab === 'why' ? null : tab === 'rounds' ? (
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
            <select className="field" style={{ flex: '0 1 160px', width: 'auto' }} value={st} onChange={e => { setSt(e.target.value); setPage(0); }} aria-label="Outcome"><option value="">Any outcome</option><option value="sold">Sold / closed</option><option value="unsold">No bidders</option><option value="CANCELLED">Cancelled</option><option value="final">Has a known final bid</option></select>
          </div>
          <div className="tbl-wrap"><table className="tbl">
            <thead><tr><th>Bid date</th><th>Lot</th><th>Locality</th><th className="n">Base ₹/m²</th><th className="n">Bidders</th><th className="n">Final bid ₹/m²</th><th>Outcome</th></tr></thead>
            <tbody>{lots.slice(page * PER, page * PER + PER).map(l => { const s = STATUS[l.status] ?? [l.status, '']; return (
              <tr key={l.no}><td className="mono small" style={{ whiteSpace: 'nowrap' }}>{fmtDate(l.date)}</td><td>{l.title}<br /><span className="tiny muted">{l.no}</span></td><td className="small">{l.locality ?? '—'}</td>
                <td className="n">{l.bidderCount ?? '—'}</td>
                <td className="n">{l.final ? <span title={`From BDA's ${l.finalFrom} result table`}>{l.final.toLocaleString('en-IN')}{l.base ? <><br /><span className="tiny muted">+{Math.round((l.final / l.base - 1) * 100)}%{l.rejected ? ' · rej' : ''}</span></> : null}</span> : '—'}</td>
                <td><span className={`pill ${s[1]}`}>{s[0]}</span>{l.reason && <div className="tiny muted" style={{ marginTop: 4, maxWidth: 220 }}>{l.reason}</div>}</td></tr>); })}</tbody>
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
