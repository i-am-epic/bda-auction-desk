import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useData } from '../lib/data';
import { applyFilters, activeCount, BUDGET_MAX, CHIPS, DEFAULT_FILTERS, fromParams, SORTS, toParams, type Filters } from '../lib/filters';
import { inr } from '../lib/format';
import { SiteCard, Icon } from '../components/ui';
import { ExploreMap } from '../components/MapView';

export default function Explore() {
  const { sites } = useData();
  const [params, setParams] = useSearchParams();
  const f = useMemo(() => fromParams(params), [params]);
  const set = (patch: Partial<Filters>) => setParams(toParams({ ...f, ...patch }), { replace: true });
  const [open, setOpen] = useState(false);
  const [view, setView] = useState<'list' | 'map'>('list');
  const [hover, setHover] = useState<string | null>(null);
  const list = useMemo(() => applyFilters(sites, f), [sites, f]);
  const n = activeCount(f);

  return (
    <div className="explore" data-view={view}>
      {open && <div className="scrim" onClick={() => setOpen(false)} />}
      <aside className={`fpanel ${open ? 'open' : ''}`} aria-label="Filters">
        <div className="inner">
          <div className="row"><h3>Filters</h3><span className="spacer" />
            {n > 0 && <button className="btn sm ghost" onClick={() => setParams(toParams({ ...DEFAULT_FILTERS, sort: f.sort }), { replace: true })}>Clear {n}</button>}
            <button className="btn sm fbtn-m" onClick={() => setOpen(false)}>Done</button></div>
          <div className="fgroup"><label htmlFor="q">Search</label>
            <input id="q" className="field" type="search" value={f.q} placeholder="Site no., layout or KPPP no." onChange={e => set({ q: e.target.value })} /></div>
          <div className="fgroup range"><span className="lab">Budget (all-in at the likely price)</span>
            <input aria-label="Maximum budget" type="range" min={10} max={BUDGET_MAX} step={5} value={f.budgetMax} onChange={e => set({ budgetMax: Number(e.target.value) })} />
            <div className="vals"><span>₹10 L</span><b>{f.budgetMax >= BUDGET_MAX ? 'Any budget' : `up to ${inr(f.budgetMax * 1e5)}`}</b><span>₹6 Cr+</span></div></div>
          <div className="fgroup"><span className="lab">Show only</span>
            <div className="chipset">{CHIPS.map(c => (
              <label key={c.key} className="chip"><input type="checkbox" checked={f[c.key] as boolean} onChange={e => set({ [c.key]: e.target.checked } as Partial<Filters>)} />{c.label}</label>))}</div></div>
          <div className="fgrid">
            <div className="fgroup"><label htmlFor="zone">Zone</label><select id="zone" className="field" value={f.zone} onChange={e => set({ zone: e.target.value })}><option value="">All</option><option>South</option><option>West</option><option>North</option></select></div>
            <div className="fgroup"><label htmlFor="verdict">Rating</label><select id="verdict" className="field" value={f.verdict} onChange={e => set({ verdict: e.target.value })}><option value="">All</option><option>Strong buy</option><option>Good</option><option>Fair / selective</option><option>Skip / high risk</option><option>Withdrawn</option></select></div>
            <div className="fgroup"><label htmlFor="growth">Area growth</label><select id="growth" className="field" value={f.growth} onChange={e => set({ growth: e.target.value })}><option value="">Any</option><option value="Strong">Strong</option><option value="Steady+">Steady or better</option><option value="Slow">Slow only</option></select></div>
            <div className="fgroup"><label htmlFor="comp">Competition</label><select id="comp" className="field" value={f.comp} onChange={e => set({ comp: e.target.value })}><option value="">Any</option><option value="2.4">Low</option><option value="3.4">Moderate or less</option></select></div>
            <div className="fgroup"><label htmlFor="size">Plot size</label><select id="size" className="field" value={f.size} onChange={e => set({ size: e.target.value })}><option value="">Any</option><option value="s">Under 600 ft²</option><option value="m">600–1,500 ft²</option><option value="l">1,500–3,000 ft²</option><option value="xl">3,000 ft²+</option></select></div>
            <div className="fgroup"><label htmlFor="facing">Facing</label><select id="facing" className="field" value={f.facing} onChange={e => set({ facing: e.target.value })}><option value="">Any</option><option value="EN">East / North / NE</option><option value="SW">South / West / SW</option></select></div>
            <div className="fgroup" style={{ gridColumn: '1 / -1' }}><label htmlFor="road">Road width</label><select id="road" className="field" value={f.road} onChange={e => set({ road: e.target.value })}><option value="">Any road</option><option value="12">12 m (40 ft) or wider</option><option value="18">18 m (60 ft) or wider</option></select></div>
          </div>
          <p className="tiny muted">Road widths, facing and prices marked * are estimates. Missing data never removes a site from a filter unfairly; it is estimated instead.</p>
        </div>
      </aside>

      <section className="results">
        <div className="bar">
          <button className="btn sm fbtn-m" onClick={() => setOpen(true)}><Icon name="filter" size={16} />Filters{n > 0 && ` · ${n}`}</button>
          <b className="num">{list.length}</b><span className="muted small">sites</span>
          <span className="spacer" />
          <label className="small muted sort-l" htmlFor="sort">Sort</label>
          <select id="sort" className="field" style={{ width: 'auto', height: 34 }} value={f.sort} onChange={e => set({ sort: e.target.value })}>
            {SORTS.map(s => <option key={s.key} value={s.key}>{s.label}</option>)}
          </select>
          <div className="seg mobile-switch" role="tablist" style={{ width: '100%' }}>
            <button role="tab" aria-selected={view === 'list'} className={view === 'list' ? 'on' : ''} style={{ flex: 1 }} onClick={() => setView('list')}>List</button>
            <button role="tab" aria-selected={view === 'map'} className={view === 'map' ? 'on' : ''} style={{ flex: 1 }} onClick={() => setView('map')}>Map</button>
          </div>
        </div>
        <div className="list">
          {list.map(s => <SiteCard key={s.id} s={s} selected={hover === s.id} onHover={setHover} />)}
          {!list.length && <div className="empty-state"><h3>No sites match</h3><p>Raise the budget or clear a filter.</p></div>}
        </div>
      </section>

      <div className="mapbox">
        <ExploreMap sites={list} hover={hover} />
        <div className="legend" aria-hidden="true">
          <span className="v-strong"><i />Strong buy</span><span className="v-good"><i />Good</span><span className="v-fair"><i />Fair</span><span className="v-skip"><i />Skip</span>
          <span><i className="dash" />Outline drawn from notice</span>
        </div>
      </div>
    </div>
  );
}
