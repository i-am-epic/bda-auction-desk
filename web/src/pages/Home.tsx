import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAP, useData } from '../lib/data';
import { RANKINGS, ranked } from '../lib/rank';
import { fmtDate, rs } from '../lib/format';
import { SiteCard, Icon } from '../components/ui';

function useCountdown(iso?: string) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 60000); return () => clearInterval(t); }, []);
  if (!iso) return null;
  const ms = new Date(iso).getTime() - now;
  if (ms <= 0) return null;
  return { d: Math.floor(ms / 864e5), h: Math.floor((ms % 864e5) / 36e5), m: Math.floor((ms % 36e5) / 6e4) };
}

const PICK_TABS = ['score', 'value', 'growth', 'odds', 'rental', 'commercial', 'cheap'];

export default function Home() {
  const { active, meta } = useData();
  const ap = useAP();
  const [rk, setRk] = useState('score');
  const cd = useCountdown(meta?.auction.eoiDeadline);
  const top = useMemo(() => ranked(active.filter(s => s.verdict !== 'Skip / high risk'), rk).slice(0, 6), [active, rk]);
  if (!meta) return null;
  const rank = RANKINGS.find(r => r.key === rk)!;
  const count = (v: string) => active.filter(s => s.verdict === v).length;
  const relisted = active.filter(s => s.prevRounds.length).length;
  const unsoldBefore = active.filter(s => s.prevRounds.some(p => p.status.startsWith('NO_'))).length;
  const cut = active.filter(s => (s.baseChange ?? 0) <= -10).sort((a, b) => (a.baseChange ?? 0) - (b.baseChange ?? 0))[0];
  const groups = Object.values(meta.groups);
  const lowSell = groups.filter(g => g.history && g.history.lots >= 15).sort((a, b) => a.history!.sellThrough - b.history!.sellThrough)[0];
  const bidEnd = meta.auction.bidDays[meta.auction.bidDays.length - 1]?.date;

  return (
    <>
      <section className="hero">
        <svg className="hero-plat" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
          <g fill="none" stroke="#e3a032" strokeWidth="1.2">
            {Array.from({ length: 14 }).map((_, i) => <path key={i} d={`M${-40 + i * 64} 420 L${40 + i * 64} -20`} />)}
            {Array.from({ length: 9 }).map((_, i) => <path key={`h${i}`} d={`M-20 ${i * 52} L820 ${i * 52 - 60}`} />)}
          </g>
        </svg>
        <div className="wrap">
          <div>
            <div className="eyebrow">Analysis of BDA e-auction {meta.auction.code} · {meta.auction.notice}</div>
            <h1>{active.length} plots. <em>{active.filter(s => s.greatFind).length} worth fighting for.</em></h1>
            <p className="lead">Every site in this auction, rated 0–10 on value after the likely winning bid, growth, location, usability and your odds of winning.</p>
            <div className="cta">
              <Link to={ap('/explore')} className="btn gold">Explore all {active.length} sites <Icon name="map" size={16} /></Link>
              <Link to={ap('/explore?great=true')} className="btn ghost">Great finds only</Link>
            </div>
          </div>
          <div className="countdown">
            <div className="eyebrow" style={{ color: 'inherit', opacity: .7 }}>Key dates</div>
            {cd ? <div className="big"><b>{cd.d}d {cd.h}h {cd.m}m</b><span>to register interest on KPPP and pay the ₹4 L EMD per site (closes {fmtDate(meta.auction.eoiDeadline)}, 5 pm)</span></div>
              : <div className="big"><b>Registration closed</b><span>{bidEnd && new Date(bidEnd) >= new Date(new Date().toDateString()) ? 'Bidding is on the days below.' : 'This auction has finished.'}</span></div>}
            <div className="timeline-mini">
              {meta.auction.bidDays.map(b => <div key={b.date}><small>{b.range}</small><b>{fmtDate(b.date).replace(/ 20\d\d$/, '')}, 10–4</b></div>)}
            </div>
          </div>
        </div>
      </section>

      <div className="wrap">
        <div className="stats">
          <div><b className="num">{active.length}</b><span>sites on sale</span></div>
          <div><b className="num" style={{ color: 'var(--strong)' }}>{count('Strong buy')}</b><span>strong buys</span></div>
          <div><b className="num" style={{ color: 'var(--good)' }}>{count('Good')}</b><span>good</span></div>
          <div><b className="num" style={{ color: 'var(--fair)' }}>{count('Fair / selective')}</b><span>fair</span></div>
          <div><b className="num" style={{ color: 'var(--skip)' }}>{count('Skip / high risk')}</b><span>skip</span></div>
          <div><b className="num">{relisted}</b><span>auctioned before</span></div>
        </div>

        <section className="section">
          <div className="section-h"><div><div className="eyebrow">Top picks in {meta.auction.code}</div><h2>{rank.label}</h2></div><p>{rank.blurb}</p></div>
          <div className="scroller" role="tablist">
            {PICK_TABS.map(k => RANKINGS.find(r => r.key === k)!).map(r => <button key={r.key} role="tab" aria-selected={rk === r.key} className={`tabchip ${rk === r.key ? 'on' : ''}`} onClick={() => setRk(r.key)}>{r.label}</button>)}
          </div>
          <div className="picks-grid">{top.map(s => <SiteCard key={s.id} s={s} />)}</div>
          <div style={{ marginTop: 16 }}><Link to={ap(`/explore?sort=${rk}`)} className="btn">Full ranking and more sorts</Link></div>
        </section>

        <section className="section" style={{ paddingTop: 0 }}>
          <div className="section-h"><div><div className="eyebrow">From BDA's own records on KPPP</div><h2>Three things to know</h2></div>
            <Link to="/history" className="btn sm">See every past auction</Link></div>
          <div className="insights">
            <div className="card insight"><b className="num">{relisted}/{active.length}</b><p>sites were in an earlier BDA auction, and {unsoldBefore} drew no bidders at least once. Expect fewer rivals, but find out why each didn't sell.</p></div>
            {cut && <div className="card insight"><b className="num">{cut.baseChange}%</b><p>BDA cut the base on <Link to={ap(`/site/${cut.id}`)}>Site {cut.site}</Link> ({cut.locality}) after it went unsold: {rs(cut.prevBase)} → {rs(cut.rate)}/m².</p></div>}
            {lowSell && <div className="card insight"><b className="num">{lowSell.history!.sellThrough}%</b><p>of past lots sold in {lowSell.name}, the lowest sell-through here. Bidding there tends to be thin.</p></div>}
          </div>
        </section>

        <section className="section" style={{ paddingTop: 0 }}>
          <div className="section-h"><div><div className="eyebrow">{groups.length} areas</div><h2>Where the best sites are</h2></div>
            <Link to={ap('/localities')} className="btn sm">All localities</Link></div>
          <div className="loc-grid">
            {[...groups].sort((a, b) => (b.bestScore ?? 0) - (a.bestScore ?? 0)).slice(0, 6).map(g => (
              <Link key={g.id} to={ap(`/localities/${g.id}`)} className="card loc-card">
                <div className="row" style={{ justifyContent: 'space-between' }}><span className={`growth-tag g-${g.growth.replace(' ', '-')}`}>{g.growth} growth</span><span className="tiny muted">{g.sites} site{g.sites === 1 ? '' : 's'}</span></div>
                <h3>{g.name}</h3>
                <div className="kv"><span>Best rating here</span><b>{g.bestScore ?? '—'}/10</b></div>
                <div className="kv"><span>Past lots sold</span><b>{g.history ? `${g.history.sellThrough}%` : '—'}</b></div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
