export type Sev = 'bad' | 'warn' | 'info';
export interface Flag { sev: Sev; text: string }
export interface Round { date: string; status: string; base: number | null; no: string; reason?: string | null; final?: number | null }
export interface Project { kind: 'boost' | 'concern'; name: string; status: string; effect: string; src: string }
export interface Persona { who: string; fit: 'Good fit' | 'Possible' | 'Weak fit'; think: string }
export interface Commercial {
  usableM2: number; gfSqft: number; upperSqft: number; rent: number; build: number; incomeValue: number;
  rate: number; wedge: boolean; frontage: number; depth: number; road: string;
}
export interface Road {
  width: number; range?: [number, number]; ft: number; far: number; source: string; conf: 'Mapped' | 'Estimated*';
  planned?: { width: number; dist: number; inside: boolean; source: string };
}
export interface Growth { label: string; cagr: number; drivers: string[]; watch: string[]; story: string; ask: string }
export type Verdict = 'Strong buy' | 'Good' | 'Fair / selective' | 'Skip / high risk' | 'Withdrawn';

export interface Site {
  id: string; sl: string; site: string; layout: string; zone: 'South' | 'West' | 'North'; group: string; locality: string;
  source: string; status: 'active' | 'withdrawn'; ew: string; ns: string; area: number; area_corr?: number | null; areaSqft: number;
  rate: number; ratePerSqft: number; baseTotal: number; minBidRate: number; minBidTotal: number;
  expRate: number; expTotal: number; expLo: number; expHi: number; expPremium: number; maxBidRate: number; maxBidTotal: number;
  fairRate: number; fairLo: number; fairHi: number; fairSqft: number; fairTotal: number; marketSqft: [number, number, number];
  upside: number; headroomAtExp?: number; premiumOverBase: number; valueBasis: string;
  competition: number; compLabel: string; bidders: string; winChance: number; noBidRisk: number;
  stampReg: number; tds: number; allIn: number; buildCost: number; projectCost: number; builtUpSqft: number; floors: string; far: number; use: string;
  rentMonthly: number; rentalYield: number; commercialYield: number | null; resaleReturn: number | null; value5y: number; gain5y: number;
  score: number | null; scoreParts?: Record<'value' | 'growth' | 'location' | 'usability' | 'confidence' | 'odds', number>;
  verdict: Verdict; greatFind: boolean; sleeper: boolean;
  flags: Flag[]; surroundRisks: Flag[]; surroundGoods: string[]; vastu: { kind: 'good' | 'bad' | 'neutral'; text: string }[];
  findings: string[]; description: string; personas: Persona[]; pros: string[]; cons: string[];
  kppp: { no: string; id: number; title: string } | null; prevRounds: Round[]; prevBase: number | null; baseChange: number | null;
  marketCap: { rate: number; base: number; date: string; applied?: boolean } | null;
  commercial: Commercial | null; road: Road; metro: { name: string; km: number }; hubs: { name: string; km: number }[];
  growth: Growth; projects: Project[]; geotag: 'official' | 'approx'; geoNote?: string; polyArea?: number; polyDrawn?: boolean;
  irregularity: number; usability: number; tier: number; lat: number; lon: number; polygon: [number, number][];
  terrain: { elev?: number; slope?: number; aspect?: string; relief?: number; facing?: string | null; frontage?: string; frontageM?: number };
  near: Record<string, { m: number; name: string }>; bidDay: string | null;
  pSell: number | null; comps: { n: number; medianSqft: number; p25: number; p75: number } | null; placement?: 'pin' | 'adjacent' | 'locality' | null;
}

export interface LocalityHistory { lots: number; sold: number; unsold: number; sellThrough: number; baseSeries: [number, number][]; baseCagr: number | null }
export interface Locality {
  id: string; name: string; lo: number; mid: number; hi: number; tier: number; cagr: number; growth: string; demand: number;
  ask: string; story: string; drivers: string[]; watch: string[]; history?: LocalityHistory; projects: Project[]; sites: number;
  center: [number, number]; bestScore: number | null; baseRates: number[];
}
export interface Meta {
  auction: {
    code: string; notice: string; noticeDate: string; eoiDeadline: string; bidDays: { date: string; range: string }[];
    emd: number; fee: number; notice_pdf: string; corrigendum_pdf: string; kppp: string; helpline: string; id: string; title: string; status: string; geotag_url: string;
  };
  generated: string; groups: Record<string, Locality>; calibration: { note: string; src: string };
  models?: { premium: ModelPremium; sell: ModelSell } | null;
}

export interface AuctionIndex {
  id: string; code: string; title: string; notice: string; noticeDate: string; eoiDeadline: string;
  bidDays: { date: string; range: string }[]; status: string; sites: number; strong: number; great: number; localities: number; generated: string;
}
export interface HistoryLot { date: string; status: string; base: number | null; title: string; no: string; group: string | null; locality: string | null; site: string | null; reason?: string | null; cancelledOn?: string | null; final?: number | null; finalFrom?: string | null }
export interface HistoryRound {
  month: string; start: string; end: string; lots: number; sold: number; unsold: number; cancelled: number; upcoming: number;
  medianBase: number | null; minBase: number | null; maxBase: number | null; localities: [string, number, number][];
}
export interface History {
  rounds: HistoryRound[]; lots: HistoryLot[]; note: string; finalsKnown: number;
  cancellations: [string, { date: string; title: string; no: string; reason: string | null; locality: string | null }[]][];
  summary: { lots: number; sold: number; unsold: number; relistedSites: number; uniqueSites: number; first: string; last: string };
}

export interface ModelPremium { n: number; alpha: number; cvMaePts: number; baselineGlobalPts: number; baselineOldRulePts: number; sigma: number; q10: number; q90: number; coef: Record<string, number>; medianPremium: number; auctions: string[] }
export interface ModelSell { nTrain: number; nTest: number; auc: number; brier: number; brierBase: number; n: number; soldRate: number; coef: Record<string, number> }
