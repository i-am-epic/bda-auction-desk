import type { Site } from './types';
import { RANKINGS, ranked } from './rank';

export interface Filters {
  q: string; budgetMax: number; budgetMin: number; zone: string; verdict: string; growth: string; comp: string; size: string;
  facing: string; road: string; sort: string;
  commercial: boolean; previous: boolean; fresh: boolean; great: boolean; sleeper: boolean; clean: boolean; approx: boolean; added: boolean; withdrawn: boolean;
  sold: boolean; nobids: boolean;
}
export const BUDGET_MAX = 600; // lakh; slider top means "any"
export const DEFAULT_FILTERS: Filters = {
  q: '', budgetMax: BUDGET_MAX, budgetMin: 0, zone: '', verdict: '', growth: '', comp: '', size: '', facing: '', road: '', sort: 'score',
  commercial: false, previous: false, fresh: false, great: false, sleeper: false, clean: false, approx: false, added: false, withdrawn: false,
  sold: false, nobids: false,
};
export const CHIPS: { key: keyof Filters; label: string }[] = [
  { key: 'sold', label: 'Sold (drew bids)' }, { key: 'nobids', label: 'No bids' },
  { key: 'great', label: 'Great finds' }, { key: 'sleeper', label: 'Sleepers' }, { key: 'commercial', label: 'Commercial potential' },
  { key: 'previous', label: 'Auctioned before' }, { key: 'fresh', label: 'First time on auction' }, { key: 'clean', label: 'No red flags' },
  { key: 'approx', label: 'Not on BDA map' }, { key: 'added', label: 'Added by corrigendum' }, { key: 'withdrawn', label: 'Show withdrawn' },
];
export const SORTS = RANKINGS.map(r => ({ key: r.key, label: r.label })).concat([{ key: 'size', label: 'Largest plot' }, { key: 'sl', label: 'Notice order' }]);

export const hasRedFlag = (s: Site) => [...s.flags, ...s.surroundRisks].some(f => f.sev === 'bad');
export const commercialOk = (s: Site) => !!s.commercial && s.commercial.gfSqft >= 85;

export function activeCount(f: Filters): number {
  return (Object.keys(DEFAULT_FILTERS) as (keyof Filters)[]).filter(k => k !== 'sort' && f[k] !== DEFAULT_FILTERS[k]).length;
}

export function applyFilters(all: Site[], f: Filters): Site[] {
  const q = f.q.trim().toLowerCase();
  const showW = f.withdrawn || f.verdict === 'Withdrawn';
  const out = all.filter(s => {
    if (!showW && s.status !== 'active') return false;
    if (f.zone && s.zone !== f.zone) return false;
    if (f.verdict && s.verdict !== f.verdict) return false;
    if (f.budgetMax < BUDGET_MAX && s.allIn > f.budgetMax * 1e5) return false;
    if (f.budgetMin > 0 && s.allIn < f.budgetMin * 1e5) return false;
    if (f.growth === 'Strong' && s.growth.label !== 'Strong') return false;
    if (f.growth === 'Steady+' && !['Strong', 'Steady', 'Mature'].includes(s.growth.label)) return false;
    if (f.growth === 'Slow' && !s.growth.label.startsWith('Slow')) return false;
    if (f.comp && s.competition >= Number(f.comp)) return false;
    if (f.size === 's' && s.areaSqft >= 600) return false;
    if (f.size === 'm' && (s.areaSqft < 600 || s.areaSqft >= 1500)) return false;
    if (f.size === 'l' && (s.areaSqft < 1500 || s.areaSqft >= 3000)) return false;
    if (f.size === 'xl' && s.areaSqft < 3000) return false;
    const fc = s.terrain.facing || '';
    if (f.facing === 'EN' && !['East', 'North', 'North-East'].includes(fc)) return false;
    if (f.facing === 'SW' && !['South', 'West', 'South-West'].includes(fc)) return false;
    if (f.road && (s.road?.width || 0) < Number(f.road)) return false;
    if (f.commercial && !commercialOk(s)) return false;
    if (f.previous && !s.prevRounds.length) return false;
    if (f.fresh && s.prevRounds.length) return false;
    if (f.great && !s.greatFind) return false;
    if (f.sleeper && !s.sleeper) return false;
    if (f.clean && hasRedFlag(s)) return false;
    if (f.approx && s.geotag !== 'approx') return false;
    if (f.added && !s.source.startsWith('Corr')) return false;
    if (f.sold && s.outcome?.status !== 'sold') return false;
    if (f.nobids && s.outcome?.status !== 'nobids') return false;
    if (q && !`${s.site} ${s.layout} ${s.locality} ${s.kppp?.no ?? ''}`.toLowerCase().includes(q)) return false;
    return true;
  });
  if (f.sort === 'size') return out.sort((a, b) => b.area - a.area);
  if (f.sort === 'sl') return out.sort((a, b) => slNum(a) - slNum(b));
  const r = ranked(out, f.sort);
  return r.concat(out.filter(s => !r.includes(s)));
}
const slNum = (s: Site) => (s.sl.startsWith('C') ? 200 + Number(s.sl.slice(1)) : Number(s.sl));

/** filters <-> URL search params so a filtered view can be bookmarked or shared */
export function toParams(f: Filters): URLSearchParams {
  const p = new URLSearchParams();
  (Object.keys(f) as (keyof Filters)[]).forEach(k => { if (f[k] !== DEFAULT_FILTERS[k]) p.set(k, String(f[k])); });
  return p;
}
export function fromParams(p: URLSearchParams): Filters {
  const f: Filters = { ...DEFAULT_FILTERS };
  (Object.keys(DEFAULT_FILTERS) as (keyof Filters)[]).forEach(k => {
    const v = p.get(k); if (v == null) return;
    const d = DEFAULT_FILTERS[k];
    (f as unknown as Record<string, unknown>)[k] = typeof d === 'boolean' ? v === 'true' : typeof d === 'number' ? Number(v) : v;
  });
  return f;
}
