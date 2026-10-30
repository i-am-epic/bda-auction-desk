import { useSyncExternalStore } from 'react';

const KEY = 'bda-shortlist';
let ids: string[] = (() => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; } })();
const subs = new Set<() => void>();
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(ids)); } catch { /* private mode */ } subs.forEach(f => f()); };

export const shortlist = {
  toggle(id: string) { ids = ids.includes(id) ? ids.filter(x => x !== id) : [...ids, id]; save(); },
  remove(id: string) { ids = ids.filter(x => x !== id); save(); },
  clear() { ids = []; save(); },
};
export function useShortlist(): string[] {
  return useSyncExternalStore(f => { subs.add(f); return () => subs.delete(f); }, () => ids);
}
