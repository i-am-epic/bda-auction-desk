import { NavLink, Link, Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { useShortlist } from '../lib/shortlist';
import { useAuctions, useCurrentAuctionId } from '../lib/data';
import { fmtDate } from '../lib/format';
import { Icon } from './ui';

const Logo = () => (
  <svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#173f31" stroke="rgba(255,255,255,.2)" /><path d="M14 46V20l14 8v18M30 46V24l20-8v30" fill="none" stroke="#e3a032" strokeWidth="5" strokeLinejoin="round" /></svg>
);

export default function Layout() {
  const loc = useLocation();
  const auctions = useAuctions();
  const current = useCurrentAuctionId();
  const aid = loc.pathname.match(/^\/a\/([^/]+)/)?.[1] ?? current;
  const a = auctions?.find(x => x.id === aid);
  const list = useShortlist().filter(k => k.startsWith(`${aid}/`));
  useEffect(() => { if (!loc.hash) window.scrollTo(0, 0); }, [loc.pathname, loc.hash]);
  const base = `/a/${aid}`;
  const links = [
    { to: base, label: 'Overview', icon: 'home', end: true },
    { to: `${base}/explore`, label: 'Explore', icon: 'map' },
    { to: `${base}/localities`, label: 'Localities', icon: 'grid' },
    { to: `${base}/shortlist`, label: 'Shortlist', icon: 'star', count: list.length },
    { to: '/history', label: 'Past auctions', short: 'History', icon: 'clock' },
  ];
  const inAuction = loc.pathname.startsWith('/a/');
  return (
    <>
      <header className="hdr">
        <div className="wrap">
          <Link to={base} className="logo"><Logo />BDA Auction Desk</Link>
          <nav className="nav" aria-label="Main">
            {links.map(l => <NavLink key={l.to} to={l.to} end={l.end}>{l.label}{!!l.count && <span className="count">{l.count}</span>}</NavLink>)}
            <NavLink to="/method">Method</NavLink>
          </nav>
          <a className="btn gold sm hdr-cta" href="https://kppp.karnataka.gov.in/#/portal/Auctions/live" target="_blank" rel="noopener"><span className="lbl-long">Bid on </span>KPPP <Icon name="ext" size={14} /></a>
        </div>
      </header>
      {a && (
        <div className="aband">
          <div className="wrap">
            <span className="pill gold">{a.code}</span>
            <span className="aband-t">{inAuction ? 'You are viewing' : 'Current'}: <b>{a.title}</b>
              <span className="aband-d"> · notice {fmtDate(a.noticeDate)} · bidding {a.bidDays.map(d => fmtDate(d.date).replace(/ 20\d\d$/, '')).join(', ')}</span></span>
            <span className="spacer" />
            {(auctions?.length ?? 0) > 1 ? <Link to="/auctions" className="aband-l">Switch auction</Link> : <Link to="/auctions" className="aband-l">All auctions</Link>}
          </div>
        </div>
      )}
      <main><Outlet /></main>
      {!loc.pathname.includes('/explore') && (
        <footer className="ftr">
          <div className="wrap">
            <span>Decision support, not a valuation or legal opinion. Verify every figure with BDA, a registered valuer and a lawyer.</span>
            <span>Each auction is analysed on its own notice; figures marked * are estimates.</span>
            <Link to="/method">How it works</Link>
            <a href="https://github.com/i-am-epic/bda-auction-desk" target="_blank" rel="noopener">Source on GitHub</a>
          </div>
        </footer>
      )}
      <nav className="tabbar" aria-label="Main">
        {links.map(l => <NavLink key={l.to} to={l.to} end={l.end}><Icon name={l.icon} />{l.short ?? l.label}{!!l.count && <span className="count">{l.count}</span>}</NavLink>)}
      </nav>
    </>
  );
}
