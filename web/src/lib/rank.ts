import type { Site } from './types';

export interface Ranking { key: string; label: string; blurb: string; value: (s: Site) => number | null; fmt: (s: Site) => string; asc?: boolean }

const p = (v: number | null | undefined, d = 1) => (v == null ? '—' : `${v.toFixed(d)}%`);
export const RANKINGS: Ranking[] = [
  { key: 'score', label: 'Best overall', blurb: 'Our 0–10 rating: value, growth, location, usability, confidence and odds.', value: s => s.score, fmt: s => `${s.score}/10` },
  { key: 'value', label: 'Best value', blurb: 'Most headroom left after paying the expected winning bid.', value: s => s.headroomAtExp ?? null, fmt: s => `${p(s.headroomAtExp ?? null, 0)} headroom` },
  { key: 'location', label: 'Best location', blurb: 'Locality tier and metro distance.', value: s => s.scoreParts?.location ?? null, fmt: s => `${s.metro.km} km to metro` },
  { key: 'growth', label: 'Best growth', blurb: 'Expected yearly land appreciation for the area.', value: s => s.growth.cagr, fmt: s => `~${s.growth.cagr}%/yr` },
  { key: 'usability', label: 'Most usable', blurb: 'Size and shape that build out cleanly.', value: s => s.scoreParts?.usability ?? null, fmt: s => `${s.areaSqft.toLocaleString('en-IN')} ft²` },
  { key: 'rental', label: 'Rental yield', blurb: 'Gross rent on land plus construction, built as a residential rental.', value: s => s.rentalYield, fmt: s => p(s.rentalYield, 2) },
  { key: 'resale', label: 'Resale return', blurb: 'Projected yearly return if you hold 5 years and sell.', value: s => s.resaleReturn, fmt: s => `${p(s.resaleReturn)}/yr` },
  { key: 'commercial', label: 'Commercial yield', blurb: 'Shop or office rent on a wide road, after setbacks.', value: s => s.commercialYield, fmt: s => p(s.commercialYield, 2) },
  { key: 'odds', label: 'Best odds', blurb: 'Highest chance of winning at our walk-away bid.', value: s => s.winChance, fmt: s => `${s.winChance}% win` },
  { key: 'cheap', label: 'Lowest entry', blurb: 'Smallest all-in cost at the expected winning bid.', value: s => s.allIn, fmt: s => `${Math.round(s.allIn / 1e5)} L all-in`, asc: true },
];

export function ranked(sites: Site[], key: string): Site[] {
  const r = RANKINGS.find(x => x.key === key) ?? RANKINGS[0];
  return sites.filter(s => r.value(s) != null).sort((a, b) => {
    const d = (r.value(a)! - r.value(b)!) * (r.asc ? 1 : -1);
    return d !== 0 ? d : (b.score ?? 0) - (a.score ?? 0);
  });
}
