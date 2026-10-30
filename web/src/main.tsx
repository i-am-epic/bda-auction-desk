import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes, Link } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import './styles.css';
import { DataProvider, useData } from './lib/data';
import Layout from './components/Layout';
import Home from './pages/Home';
import Explore from './pages/Explore';
import SitePage from './pages/SitePage';
import { Localities, LocalityPage } from './pages/Localities';
import Shortlist from './pages/Shortlist';
import Method from './pages/Method';

function Gate({ children }: { children: React.ReactNode }) {
  const { loading, error } = useData();
  if (loading) return <div className="loading">Loading the auction…</div>;
  if (error) return <div className="loading">{error}</div>;
  return <>{children}</>;
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <DataProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Gate><Home /></Gate>} />
            <Route path="explore" element={<Gate><Explore /></Gate>} />
            <Route path="site/:id" element={<Gate><SitePage /></Gate>} />
            <Route path="localities" element={<Gate><Localities /></Gate>} />
            <Route path="localities/:id" element={<Gate><LocalityPage /></Gate>} />
            <Route path="shortlist" element={<Gate><Shortlist /></Gate>} />
            <Route path="method" element={<Method />} />
            <Route path="*" element={<div className="wrap empty-state"><h3>Page not found</h3><Link to="/">Go home</Link></div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DataProvider>
  </StrictMode>,
);
