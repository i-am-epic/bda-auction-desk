import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useParams } from 'react-router-dom';
import type { AuctionIndex, History, Meta, Site } from './types';

/* ---------- auction index (all auctions the site knows about) ---------- */
const IndexCtx = createContext<AuctionIndex[] | null>(null);
export function IndexProvider({ children }: { children: ReactNode }) {
  const [idx, setIdx] = useState<AuctionIndex[] | null>(null);
  useEffect(() => { fetch('/data/auctions.json').then(r => r.json()).then(setIdx).catch(() => setIdx([])); }, []);
  return <IndexCtx.Provider value={idx}>{children}</IndexCtx.Provider>;
}
export const useAuctions = () => useContext(IndexCtx);
/** The auction shown by default: the newest one. */
export const useCurrentAuctionId = () => useAuctions()?.[0]?.id ?? null;

/* ---------- one auction's data, cached per id ---------- */
interface DataState { aid: string; sites: Site[]; active: Site[]; meta: Meta | null; byId: Map<string, Site>; error: string | null; loading: boolean }
const cache = new Map<string, Promise<[Site[], Meta]>>();
const load = (aid: string) => {
  if (!cache.has(aid)) cache.set(aid, Promise.all([fetch(`/data/${aid}/sites.json`).then(r => { if (!r.ok) throw new Error(); return r.json(); }),
    fetch(`/data/${aid}/meta.json`).then(r => r.json())]));
  return cache.get(aid)!;
};
const Ctx = createContext<DataState>({ aid: '', sites: [], active: [], meta: null, byId: new Map(), error: null, loading: true });

export function AuctionProvider({ children }: { children: ReactNode }) {
  const { aid = '' } = useParams();
  const [state, setState] = useState<DataState>({ aid, sites: [], active: [], meta: null, byId: new Map(), error: null, loading: true });
  useEffect(() => {
    let live = true;
    setState(s => ({ ...s, aid, loading: true }));
    load(aid).then(([sites, meta]) => live && setState({ aid, sites, meta, active: sites.filter(s => s.status === 'active'), byId: new Map(sites.map(s => [s.id, s])), error: null, loading: false }))
      .catch(() => live && setState(s => ({ ...s, loading: false, error: `No data for auction "${aid}". Pick an auction from the list.` })));
    return () => { live = false; };
  }, [aid]);
  return <Ctx.Provider value={state}>{children}</Ctx.Provider>;
}
export const useData = () => useContext(Ctx);

/* ---------- past auctions (KPPP history), loaded on demand ---------- */
let histP: Promise<History> | null = null;
export function useHistory(): History | null {
  const [h, setH] = useState<History | null>(null);
  useEffect(() => { histP ??= fetch('/data/history.json').then(r => r.json()); histP.then(setH); }, []);
  return h;
}

/** Build an in-app path inside the current auction, e.g. ap('/explore') -> '/a/t15/explore'. */
export function useAP() {
  const { aid } = useData();
  return (path = '') => `/a/${aid}${path}`;
}
