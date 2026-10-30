export const SQFT = 10.7639;

export const inr = (n: number | null | undefined): string => {
  if (n == null || Number.isNaN(n)) return '—';
  if (Math.abs(n) >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
  if (Math.abs(n) >= 1e5) return `₹${(n / 1e5).toFixed(1)} L`;
  return `₹${Math.round(n).toLocaleString('en-IN')}`;
};
export const rs = (n: number | null | undefined) => (n == null ? '—' : `₹${Math.round(n).toLocaleString('en-IN')}`);
export const perSqft = (perSqm: number) => `${rs(perSqm / SQFT)}/ft²`;
export const num = (n: number) => Math.round(n).toLocaleString('en-IN');
export const pct = (n: number | null | undefined, d = 0) => (n == null ? '—' : `${n > 0 ? '+' : ''}${n.toFixed(d)}%`);

export const fmtDate = (iso: string) =>
  new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

/** KPPP style dd-mm-yyyy to "21 Jul 2025" */
export const kpppDate = (d: string) => {
  const [dd, mm, yyyy] = d.split('-').map(Number);
  return new Date(yyyy, mm - 1, dd).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};

export const VERDICT_TONE: Record<string, string> = {
  'Strong buy': 'strong', Good: 'good', 'Fair / selective': 'fair', 'Skip / high risk': 'skip', Withdrawn: 'off',
};
export const VERDICT_SHORT: Record<string, string> = {
  'Strong buy': 'Strong buy', Good: 'Good', 'Fair / selective': 'Fair', 'Skip / high risk': 'Skip', Withdrawn: 'Withdrawn',
};
