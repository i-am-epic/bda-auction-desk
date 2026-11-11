import { useEffect, useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { Site } from '../lib/types';
import { inr, VERDICT_SHORT, VERDICT_TONE } from '../lib/format';
import { shortlist, useShortlist } from '../lib/shortlist';
import { commercialOk } from '../lib/filters';
import { useAP, useData } from '../lib/data';

/** Gold asterisk marking an estimate or model output; the title explains how it was derived. */
export const Est = ({ how = 'Estimate or model output' }: { how?: string }) => <sup className="est" title={how} aria-label={`Estimate: ${how}`}>*</sup>;

export const tone = (s: Pick<Site, 'verdict'>) => `v-${VERDICT_TONE[s.verdict]}`;

export function ScoreRing({ site, size = 52 }: { site: Pick<Site, 'score' | 'verdict'>; size?: number }) {
  const r = size / 2 - 4, c = 2 * Math.PI * r, v = (site.score ?? 0) / 10;
  return (
    <div className={`ring ${tone(site)}`} style={{ width: size, height: size }} aria-label={`Rating ${site.score ?? 'none'} out of 10`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--surface-3)" strokeWidth="5" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--v)" strokeWidth="5" strokeLinecap="round" strokeDasharray={`${c * v} ${c}`} />
      </svg>
      <b style={{ fontSize: size * 0.32 }}>{site.score ?? '–'}</b>
    </div>
  );
}

export const Verdict = ({ s }: { s: Pick<Site, 'verdict'> }) => <span className={`verdict ${tone(s)}`}>{VERDICT_SHORT[s.verdict]}</span>;

/** Auction-result badge shown once bidding has closed. */
export function OutcomeBadge({ o }: { o: Site['outcome'] }) {
  if (!o) return null;
  const title = o.status === 'sold'
    ? (o.pending ? 'Bidding closed with bids — BDA confirmation pending' : 'Sold at auction')
    : 'No valid bids — drew no participation';
  return <span className={`pill ${o.status === 'sold' ? 'sold' : 'nobids'}`} title={title}>
    {o.status === 'sold' ? '● ' : '○ '}{o.label}{o.rate ? ` · ${inr(o.total!)}` : ''}{o.pending && o.status === 'sold' ? '*' : ''}
  </span>;
}

export function Meter({ label, value, max = 10, note }: { label: ReactNode; value: number; max?: number; note?: string }) {
  return (
    <div className="meter">
      <div className="lbl"><span>{label}</span><b>{note ?? value}</b></div>
      <div className="bar"><i style={{ width: `${Math.max(2, Math.min(100, (value / max) * 100))}%` }} /></div>
    </div>
  );
}

export function StarButton({ id: siteId, label = true }: { id: string; label?: boolean }) {
  const { aid } = useData();
  const id = `${aid}/${siteId}`;
  const list = useShortlist(), on = list.includes(id);
  return (
    <button type="button" className={`star-btn ${on ? 'on' : ''}`} aria-pressed={on} title={on ? 'Remove from shortlist' : 'Add to shortlist'}
      onClick={e => { e.preventDefault(); e.stopPropagation(); shortlist.toggle(id); }}>
      <Icon name={on ? 'starFill' : 'star'} />{label && <span className="sr-only" style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0 0 0 0)' }}>{on ? 'Shortlisted' : 'Shortlist'}</span>}
    </button>
  );
}

export function SiteTags({ s, max = 4 }: { s: Site; max?: number }) {
  const t: ReactNode[] = [];
  if (s.greatFind) t.push(<span key="g" className="pill gold">Great find</span>);
  else if (s.sleeper) t.push(<span key="sl" className="pill gold">Sleeper</span>);
  if (commercialOk(s)) t.push(<span key="c" className="pill accent">Commercial</span>);
  if (s.baseChange != null && s.baseChange <= -10) t.push(<span key="cut" className="pill accent">Base cut {s.baseChange}%</span>);
  else if (s.prevRounds.length) t.push(<span key="p" className="pill">Auctioned {s.prevRounds.length}×</span>);
  if (s.source.startsWith('Corr')) t.push(<span key="a" className="pill warn">Corrigendum</span>);
  if ([...s.flags, ...s.surroundRisks].some(f => f.sev === 'bad')) t.push(<span key="r" className="pill bad">Red flag</span>);
  if (s.geotag === 'approx') t.push(<span key="d" className="pill">Drawn outline</span>);
  return <div className="tags">{t.slice(0, max)}</div>;
}

export function SiteCard({ s, selected, onHover }: { s: Site; selected?: boolean; onHover?: (id: string | null) => void }) {
  const ap = useAP();
  return (
    <Link to={ap(`/site/${s.id}`)} className={`card scard ${selected ? 'sel' : ''}`} onMouseEnter={() => onHover?.(s.id)} onMouseLeave={() => onHover?.(null)}>
      <div className="top">
        <ScoreRing site={s} size={48} />
        <div style={{ minWidth: 0 }}>
          <h3>Site {s.site}</h3>
          <div className="loc">{s.locality}</div>
        </div>
        <StarButton id={s.id} />
      </div>
      <div className="row" style={{ justifyContent: 'space-between' }}><Verdict s={s} />{s.outcome ? <OutcomeBadge o={s.outcome} /> : <SiteTags s={s} max={3} />}</div>
      <div className="figs">
        <div><small>Plot</small><b>{s.areaSqft.toLocaleString('en-IN')} ft²</b></div>
        <div><small>Likely price<Est how="Expected winning bid, calibrated to past BDA auctions" /></small><b>{inr(s.expTotal)}</b></div>
        <div><small>Win odds<Est how="Chance our walk-away bid beats every expected rival" /></small><b>{s.winChance}%</b></div>
      </div>
    </Link>
  );
}

export function Sparkline({ series, w = 140, h = 36 }: { series: [number, number][]; w?: number; h?: number }) {
  if (!series || series.length < 2) return null;
  const vs = series.map(x => x[1]), mn = Math.min(...vs), mx = Math.max(...vs);
  const sx = (i: number) => 4 + (i * (w - 8)) / (series.length - 1), sy = (v: number) => (mx === mn ? h / 2 : h - 5 - ((v - mn) / (mx - mn)) * (h - 10));
  const pts = series.map((x, i) => `${sx(i)},${sy(x[1])}`).join(' ');
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true" style={{ display: 'block', maxWidth: '100%' }}>
      <polyline points={`${sx(0)},${h} ${pts} ${sx(series.length - 1)},${h}`} fill="var(--accent-weak)" stroke="none" />
      <polyline points={pts} fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinejoin="round" />
      {series.map((x, i) => <circle key={i} cx={sx(i)} cy={sy(x[1])} r={i === series.length - 1 ? 3.5 : 2.2} fill="var(--accent)" />)}
    </svg>
  );
}

export function useToast(): [ReactNode, (t: string) => void] {
  const [msg, setMsg] = useState<string | null>(null);
  useEffect(() => { if (!msg) return; const t = setTimeout(() => setMsg(null), 2000); return () => clearTimeout(t); }, [msg]);
  return [msg ? <div className="toast" role="status">{msg}</div> : null, setMsg];
}

const PATHS: Record<string, string> = {
  home: 'M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z',
  map: 'M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2zm0 0v14m6-12v14',
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
  star: 'M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z',
  starFill: 'M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z',
  info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zm0-11v6m0-9v.01',
  filter: 'M4 5h16M7 12h10M10 19h4',
  ext: 'M14 4h6v6m0-6L10 14M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5',
  copy: 'M9 9h10v10H9zM5 15V5h10',
  back: 'M15 18l-6-6 6-6',
  layers: 'M12 3 2 8l10 5 10-5-10-5zm-10 9 10 5 10-5M2 16l10 5 10-5',
  clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zm0-14v5l3 2',
};
export function Icon({ name, size }: { name: keyof typeof PATHS | string; size?: number }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} fill={name === 'starFill' ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={PATHS[name]} />
    </svg>
  );
}
