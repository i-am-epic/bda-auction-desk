import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Meta, Site } from './types';

interface DataState { sites: Site[]; active: Site[]; meta: Meta | null; byId: Map<string, Site>; error: string | null; loading: boolean }
const empty: DataState = { sites: [], active: [], meta: null, byId: new Map(), error: null, loading: true };
const Ctx = createContext<DataState>(empty);

export function DataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DataState>(empty);
  useEffect(() => {
    Promise.all([fetch('/data/sites.json').then(r => r.json()), fetch('/data/meta.json').then(r => r.json())])
      .then(([sites, meta]: [Site[], Meta]) =>
        setState({ sites, meta, active: sites.filter(s => s.status === 'active'), byId: new Map(sites.map(s => [s.id, s])), error: null, loading: false }))
      .catch(() => setState(s => ({ ...s, loading: false, error: 'The auction data could not load. Check your connection and reload.' })));
  }, []);
  return <Ctx.Provider value={state}>{children}</Ctx.Provider>;
}
export const useData = () => useContext(Ctx);
