import { StrictMode, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes, Link, Navigate, Outlet } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import './styles.css';
import { AuctionProvider, IndexProvider, useCurrentAuctionId, useAuctions, useData } from './lib/data';
import Layout from './components/Layout';
import Home from './pages/Home';
import Explore from './pages/Explore';
import SitePage from './pages/SitePage';
import { Localities, LocalityPage } from './pages/Localities';
import Shortlist from './pages/Shortlist';
import Method from './pages/Method';
import HistoryPage from './pages/History';
import Auctions from './pages/Auctions';

function Gate({ children }: { children: ReactNode }) {
  const { loading, error } = useData();
  if (loading) return <div className="loading">Loading the auction…</div>;
  if (error) return <div className="loading"><div className="empty-state"><h3>Auction not found</h3><p>{error}</p><p><Link to="/auctions">All auctions</Link></p></div></div>;
  return <>{children}</>;
}
function ToCurrent({ to = '' }: { to?: string }) {
  const id = useCurrentAuctionId(), list = useAuctions();
  if (!list) return <div className="loading">Loading…</div>;
  return <Navigate to={id ? `/a/${id}${to}` : '/auctions'} replace />;
}
const A = () => <AuctionProvider><Gate><Outlet /></Gate></AuctionProvider>;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <IndexProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<ToCurrent />} />
            <Route path="explore" element={<ToCurrent to="/explore" />} />
            <Route path="a/:aid" element={<A />}>
              <Route index element={<Home />} />
              <Route path="explore" element={<Explore />} />
              <Route path="site/:id" element={<SitePage />} />
              <Route path="localities" element={<Localities />} />
              <Route path="localities/:id" element={<LocalityPage />} />
              <Route path="shortlist" element={<Shortlist />} />
            </Route>
            <Route path="auctions" element={<Auctions />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="method" element={<Method />} />
            <Route path="*" element={<div className="wrap empty-state"><h3>Page not found</h3><Link to="/">Go to the current auction</Link></div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </IndexProvider>
  </StrictMode>,
);
