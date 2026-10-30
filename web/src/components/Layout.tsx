import { NavLink, Link, Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { useShortlist } from '../lib/shortlist';
import { useData } from '../lib/data';
import { Icon } from './ui';

const Logo = () => (
  <svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#173f31" stroke="rgba(255,255,255,.2)" /><path d="M14 46V20l14 8v18M30 46V24l20-8v30" fill="none" stroke="#e3a032" strokeWidth="5" strokeLinejoin="round" /></svg>
);

export default function Layout() {
  const list = useShortlist();
  const { meta } = useData();
  const loc = useLocation();
  useEffect(() => { if (!loc.hash) window.scrollTo(0, 0); }, [loc.pathname, loc.hash]);
  const links = [
    { to: '/', label: 'Home', icon: 'home', end: true },
    { to: '/explore', label: 'Explore', icon: 'map' },
    { to: '/localities', label: 'Localities', icon: 'grid' },
    { to: '/shortlist', label: 'Shortlist', icon: 'star', count: list.length },
    { to: '/method', label: 'Method', icon: 'info' },
  ];
  return (
    <>
      <header className="hdr">
        <div className="wrap">
          <Link to="/" className="logo"><Logo />BDA Auction Desk {meta && <small>{meta.auction.code}</small>}</Link>
          <nav className="nav" aria-label="Main">
            {links.map(l => <NavLink key={l.to} to={l.to} end={l.end}>{l.label}{!!l.count && <span className="count">{l.count}</span>}</NavLink>)}
          </nav>
          {meta && <a className="btn gold sm hdr-cta" href={meta.auction.kppp} target="_blank" rel="noopener"><span className="lbl-long">Bid on </span>KPPP <Icon name="ext" size={14} /></a>}
        </div>
      </header>
      <main><Outlet /></main>
      {!loc.pathname.startsWith('/explore') && (
        <footer className="ftr">
          <div className="wrap">
            <span>Decision support, not a valuation or legal opinion. Verify every figure with BDA, a registered valuer and a lawyer.</span>
            <span>Data: BDA notice T-15 and corrigendum, BDA geotag map, KPPP, OpenStreetMap, SRTM, BBMP road-width map.</span>
            <span>BDA helpline <span className="mono">9483166622</span></span>
          </div>
        </footer>
      )}
      <nav className="tabbar" aria-label="Main">
        {links.map(l => (
          <NavLink key={l.to} to={l.to} end={l.end}><Icon name={l.icon} />{l.label}{!!l.count && <span className="count">{l.count}</span>}</NavLink>
        ))}
      </nav>
    </>
  );
}
