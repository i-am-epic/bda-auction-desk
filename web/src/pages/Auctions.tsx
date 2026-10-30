import { Link } from 'react-router-dom';
import { useAuctions } from '../lib/data';
import { fmtDate } from '../lib/format';

export default function Auctions() {
  const list = useAuctions();
  if (!list) return <div className="loading">Loading auctions…</div>;
  return (
    <div className="wrap section stack" style={{ gap: 20 }}>
      <div className="section-h" style={{ marginBottom: 0 }}><div><div className="eyebrow">Analysed auctions</div><h1 style={{ fontSize: 'clamp(28px,4vw,40px)' }}>Auctions</h1></div>
        <p>Each BDA auction is analysed on its own notice and corrigendum. New auctions are added as BDA publishes them. Older rounds without a full analysis are under <Link to="/history">Past auctions</Link>.</p></div>
      <div className="picks-grid">
        {list.map((a, i) => (
          <Link key={a.id} to={`/a/${a.id}`} className="card pad stack" style={{ gap: 10, textDecoration: 'none', color: 'inherit' }}>
            <div className="row"><span className="pill gold">{a.code}</span>{i === 0 && <span className="pill accent">Latest</span>}<span className="spacer" /><span className="tiny muted">notice {fmtDate(a.noticeDate)}</span></div>
            <h3 style={{ fontSize: 20 }}>{a.title}</h3>
            <div className="small muted">Bidding {a.bidDays.map(d => fmtDate(d.date)).join(', ')}</div>
            <div className="row small"><b className="num">{a.sites}</b> sites · <b className="num" style={{ color: 'var(--strong)' }}>{a.strong}</b> strong buys · <b className="num">{a.great}</b> great finds · {a.localities} localities</div>
            <span className="tiny muted">Analysis generated {fmtDate(a.generated)}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
