import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../lib/data';
import { RANKINGS, ranked } from '../lib/rank';
import { fmtDate, rs } from '../lib/format';
import { SiteCard, Sparkline, Icon } from '../components/ui';

function useCountdown(iso?: string) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 60000); return () => clearInterval(t); }, []);
  if (!iso) return null;
  const ms = new Date(iso).getTime() - now;
  if (ms <= 0) return { past: true, d: 0, h: 0, m: 0 };
  return { past: false, d: Math.floor(ms / 864e5), h: Math.floor((ms % 864e5) / 36e5), m: Math.floor((ms % 36e5) / 6e4) };
}

export default function Home() {
  const { active, sites, meta } = useData();
  const [rk, setRk] = useState('score');
  const cd = useCountdown(meta?.auction.eoiDeadline);
  const top = useMemo(() => ranked(active.filter(s => s.verdict !== 'Skip / high risk' || rk === 'cheap'), rk).slice(0, 6), [active, rk]);
  const rank = RANKINGS.find(r => r.key === rk)!;
  if (!meta) return null;
  const count = (v: string) => active.filter(s => s.verdict === v).length;
  const relisted = active.filter(s => s.prevRounds.length).length;
  const unsoldBefore = active.filter(s => s.prevRounds.some(p => p.status.startsWith('NO_'))).length;
  const cuts = active.filter(s => (s.baseChange ?? 0) <= -10).sort((a, b) => (a.baseChange ?? 0) - (b.baseChange ?? 0));
  const groups = Object.values(meta.groups);
  const lowSell = groups.filter(g => g.history && g.history.lots >= 15).sort((a, b) => a.history!.sellThrough - b.history!.sellThrough);
  const smv = meta.groups.SMV?.history?.baseSeries;

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
            <div className="eyebrow">Bangalore Development Authority · e-auction {meta.auction.code}</div>
            <h1>{active.length} plots. <em>{active.filter(s => s.greatFind).length} worth fighting for.</em></h1>
            <p className="lead">Every site in BDA's auction, checked against its geotag map and corrigendum, priced against 2026 resale rates, and tested against BDA's own record of {groups.reduce((a, g) => a + (g.history?.lots ?? 0), 0).toLocaleString('en-IN')} past lots.</p>
            <div className="cta">
              <Link to="/explore" className="btn gold">Explore all sites <Icon name="map" size={16} /></Link>
              <Link to="/explore?great=true" className="btn ghost">See the great finds</Link>
            </div>
          </div>
          <div className="countdown">
            <div className="eyebrow" style={{ color: 'inherit', opacity: .7 }}>Register interest on KPPP by {fmtDate(meta.auction.eoiDeadline)}, 5 pm</div>
            {cd && (cd.past ? <div className="big"><b>Closed</b><span>Expression of interest window has ended</span></div>
              : <div className="big"><b>{cd.d}d {cd.h}h {cd.m}m</b><span>left to register and pay the ₹4 L EMD per site</span></div>)}
            <div className="timeline-mini">
              {meta.auction.bidDays.map(b => <div key={b.date}><small>{b.range}</small><b>{fmtDate(b.date).replace(' 2026', '')}, 10–4</b></div>)}
            </div>
          </div>
        </div>
      </section>

      <div className="wrap">
        <div className="stats">
          <div><b className="num">{active.length}</b><span>sites on sale</span></div>
          <div><b className="num" style={{ color: 'var(--strong)' }}>{count('Strong buy')}</b><span>strong buys</span></div>
          <div><b className="num" style={{ color: 'var(--good)' }}>{count('Good')}</b><span>good</span></div>
          <div><b className="num" style={{ color: 'var(--fair)' }}>{count('Fair / selective')}</b><span>fair / selective</span></div>
          <div><b className="num" style={{ color: 'var(--skip)' }}>{count('Skip / high risk')}</b><span>skip</span></div>
          <div><b className="num">{sites.length - active.length}</b><span>withdrawn</span></div>
        </div>

        <section className="section">
          <div className="section-h"><div><div className="eyebrow">Top picks</div><h2>{rank.label}</h2></div><p>{rank.blurb}</p></div>
          <div className="scroller" role="tablist">
            {RANKINGS.map(r => <button key={r.key} role="tab" aria-selected={rk === r.key} className={`tabchip ${rk === r.key ? 'on' : ''}`} onClick={() => setRk(r.key)}>{r.label}</button>)}
          </div>
          <div className="picks-grid">{top.map(s => <SiteCard key={s.id} s={s} />)}</div>
          <div style={{ marginTop: 16 }}><Link to={`/explore?sort=${rk}`} className="btn">See the full ranking</Link></div>
        </section>

        <section className="section" style={{ paddingTop: 0 }}>
          <div className="section-h"><div><div className="eyebrow">From BDA's own records</div><h2>What the data says</h2></div></div>
          <div className="insights">
            <div className="card insight"><b className="num">{relisted}/{active.length}</b><p>sites were already in an earlier BDA auction, and {unsoldBefore} drew no bidders at least once. This round is mostly leftovers: fewer rivals, but find out why each one didn't sell.</p></div>
            {cuts[0] && <div className="card insight"><b className="num">{cuts[0].baseChange}%</b><p>BDA cut the base on <Link to={`/site/${cuts[0].id}`}>Site {cuts[0].site}</Link> ({cuts[0].locality}) after three rounds with no bidders: {rs(cuts[0].prevBase)} → {rs(cuts[0].rate)}/m².</p></div>}
            {lowSell[0] && <div className="card insight"><b className="num">{lowSell[0].history!.sellThrough}%</b><p>of past lots sold in {lowSell[0].name}, the lowest sell-through here. {lowSell[1]?.name} is next at {lowSell[1]?.history!.sellThrough}%. Expect thin bidding.</p></div>}
            {smv && <div className="card insight"><b className="num">+{Math.round((smv[smv.length - 1][1] / smv[0][1] - 1) * 100)}%</b><p>rise in BDA's base rate for Sir MV Layout since {smv[0][0]}. BDA has been raising prices to follow the market.</p><Sparkline series={smv} w={220} /></div>}
            <div className="card insight"><b className="num">+62%</b><p>is what winners paid over base on average in BDA's Dec 2021 auction (296 sites). Our expected bids are calibrated to it, scaled by competition.</p></div>
          </div>
        </section>

        <section className="section" style={{ paddingTop: 0 }}>
          <div className="section-h"><div><div className="eyebrow">Where the sites are</div><h2>Localities</h2></div><p>Growth, sell-through and BDA's base-rate trend for each area in this auction.</p></div>
          <div className="loc-grid">
            {groups.sort((a, b) => (b.bestScore ?? 0) - (a.bestScore ?? 0)).map(g => (
              <Link key={g.id} to={`/localities/${g.id}`} className="card loc-card">
                <div className="row" style={{ justifyContent: 'space-between' }}><span className={`growth-tag g-${g.growth.replace(' ', '-')}`}>{g.growth} · ~{g.cagr}%/yr</span><span className="tiny muted">{g.sites} site{g.sites === 1 ? '' : 's'}</span></div>
                <h3>{g.name}</h3>
                <div className="kv"><span>Resale (mid)</span><b>₹{g.mid.toLocaleString('en-IN')}/ft²</b></div>
                <div className="kv"><span>Past lots sold</span><b>{g.history ? `${g.history.sellThrough}% of ${g.history.lots}` : '—'}</b></div>
                {g.history && g.history.baseSeries.length > 1 && <Sparkline series={g.history.baseSeries} w={240} h={30} />}
              </Link>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
