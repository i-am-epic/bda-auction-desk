# KPPP Research: 4 November 2026

## Scope and Deliverables

Public, read-only investigation of KPPP and this repository, initially compared against commit
`19e3c44904e770dd7572284b81f27eeb7c20990b`. No login, credentials, bidder identities, bid submission,
payments or CAPTCHA bypass were used. The later participant-route investigation inspected public
JavaScript only; authenticated responses were not tested.

- [Public API guide](kppp_public_api.md): 20 endpoint templates with successful sample responses.
- [Machine-readable endpoint catalogue](kppp_public_endpoints.json): methods, example requests, purposes and qualifications.
- [Public notice index](../../exports/bda_kppp_notice_index_2026-11-04.csv): 4,469 unique BDA notice IDs.
- [Supplemental checks](kppp_public_checks_2026-11-04.json): pagination, download signatures and exact export comparison.
- [Client references](kppp_client_references_2026-11-04.json): 106 HTTP call-site references and source hashes, not 106 distinct verified APIs.
- [Collector](collect_kppp_public.ps1) and [offline checks](test_collect_kppp_public.ps1).

The full-index investigation retained 73 successful API responses and the separate item-wise/corrigendum
run retained another 9. Additional browser checks verified downloads and lookup behavior. Raw responses
remain outside the committed repository because they include official contact/publishing metadata. The
committed index contains public notice metadata, not bidder records or credentials.

No exhaustive backend/OpenAPI inventory is claimed. The 106-reference inventory covers `main.js`,
`common.js` and auction-corrigendum chunk `976.js`. Other applications and lazy modules may expose more
routes. Some references are duplicates, generic helpers, translations or account-changing operations;
the collector does not automatically invoke discovered routes.

## 1. Department-Wide Coverage

Search with `departmentId: 1566` and each status, using `page` and **`size`**. The existing history collector
searches a fixed list of locality keywords. Department-wide collection avoids that restriction.

| Status | Public index | Existing history CSV |
|---|---:|---:|
| FINALIZED | 2,844 | 1,926 |
| NO_PARTICIPATIONS | 1,149 | 597 |
| NO_BIDS_RECEIVED | 194 | 112 |
| CANCELLED | 139 | 65 |
| BIDDING_CLOSED | 143 | 42 |
| PUBLISHED, LIVE_AUCTION, UNDER_EVALUATION, EVALUATED | 0 | 0 |
| Unique notice IDs | **4,469** | **2,742** |

The new index contains all 2,742 IDs from the existing CSV and **1,727 additional IDs**. This compares a
current API snapshot with the earlier repository export, so time and scope differences both matter.
The data has not been wired into the site's existing history/model outputs by this documentation PR.

These are notices, not unique plots, auction rounds or sales. Re-listings have different notice IDs.
Also classify non-property records: notice `25447` (`BDA/2026-27/AUCTION3475`) solicits interest rates for
Rs. 1,500 crore of fixed deposits. Its item units are `Percentage`, not square metres. It must not enter
a property price or sell-through model.

## 2. Pagination Correction

Against the same live-auction search body:

| Query | Rows | Total header |
|---|---:|---:|
| `page=0&pageSize=25` | 10 | 24 |
| `page=0&size=1` | 1 | 24 |
| `page=0&size=25` | 24 | 24 |
| `page=1&size=10` | 10 different records | 24 |

`pageSize` was ignored. The existing history script steps through pages of 10, matching the observed
default, so this alone does not establish a bug in its current paging. It does make increasing the old
parameter unsafe. Use `size`, check `X-Total-Count`, reject repeated/truncated pages and verify unique IDs.

## 3. Site 303: Lot-Level Evidence

Current round: `BDA/2026-27/AUCTION4491`, notice `29761`, slot `33220`, lot `38995`, item `55202`.

| Field | Observed value |
|---|---|
| Workflow status | BIDDING_CLOSED |
| Scheduled bidding | 2 Nov 2026, 10:00-16:00 |
| Recorded extended end | **2 Nov 2026, 16:47** |
| Slot delta setting | 5 minutes |
| Initial price | Rs. 84,000/m2 |
| API reserve field | Rs. 84,500/m2 |
| Increment | Rs. 500/m2 |
| EMD / fee | Rs. 400,000 / Rs. 500 |
| Participation deadline | 31 Oct 2026, 17:00 |
| Item code | BDAEAS-4222 |
| Specification | East-west `[4.50 + 10.50] / 2`, north-south 12 m, area 90 m2 |
| API quantity / net amount | **1 / 84,000**, not plot area / whole-plot price |
| `soldYn` | null |

Derived from the specification: base plot amount is Rs. 75.60 lakh and one increment is Rs. 45,000.
Your displayed Rs. 83.16 lakh minimum corresponds to `84,000 x 90 x 1.10`; the API reserve field corresponds
to Rs. 76.05 lakh. These are different concepts, not proof that the displayed minimum is wrong. The
24,210,758-byte notification PDF downloaded with a valid PDF signature, but its minimum-bid clause
could not be text-extracted. Read/OCR the authoritative notice before changing that rule.

Previous round: `BDA/2025-26/AUCTION2228`, notice `19567`, slot `21624`, lot `26874`. Its base was
Rs. 81,000/m2 and reserve Rs. 81,500/m2. The scheduled close was 20 Nov 2025 at 17:00; the recorded
extended end was **17:04**. The current base is approximately 3.70% higher.

The old notice is `FINALIZED` with `soldYn: null`. Existing signed-in evidence on the site says all bids
were rejected that round. **FINALIZED is not proof of a completed sale.** Keep workflow status, bid
approval/rejection, award and completed sale separate. A null outcome is unknown, not false or zero.

Recorded extension is useful timing evidence, not a bidder count, number of bids or proof of strong
demand. Public lot responses did not contain the winning price. Display-setting flags do not supply it.

## 4. Documents, Corrigenda and Cancellation

The additional public routes support:

- Notice attachment UUIDs, names, types and creation dates, plus binary downloads.
- Lot/item specifications, units, reserve, increments, extended closing time and force-close fields.
- Structured original/revised dates and reasons for each corrigendum, plus its documents.
- Recall reasons and recall attachment metadata.

Notice `25447` verifies the item-wise branch and two approved corrigenda (`1071`, `1072`). Corrigendum
1072 changes participation from 24 Apr 2026 at 16:00 to 27 Apr at 17:00, and bidding from 27 Apr to 29 Apr.
Its explanatory text retains the AAA credit-rating requirement and non-callable FD terms. A corrigendum
DOCX download returned 12,821 bytes with a ZIP-format signature. Order changes by evidence timestamps
and approval state, not assumed array order.

Cancelled notice `1095` records `Others` / `Technical issue` and a recall timestamp. Its document list
references `Auction_1095.json`; that attachment's contents were not downloaded. This supports distinguishing
technical cancellations from lack of participation.

The existing history pipeline already captures EMD, fees, scheduled dates, delta settings, display flags
and recall text. The main new data is wider coverage, lot/item detail, recorded extended close, document
links and structured corrigenda. Iterate all slots; the existing collector uses only the first slot.

## 5. Live Interest and Participant Counts

Do not conflate:

| Metric | Meaning | Evidence |
|---|---|---|
| Interested visitors | People considering or viewing a plot | No verified public source. |
| Submitted participants | People who submitted an EOI/participation | Participant route found in evaluation client code; access and timing unverified. |
| Actual bidders | People who placed bids | Bidder-facing client references live/past lists; completeness and authorized visibility unverified. |

Follow-up public probes of published notice `27118` and live notice `29973` returned
`displayBiddersListYn: true`, `auctionSupplierList: null` and no participant count in detail/lot payloads.
`childEntityCount` and `itemcount` count auction entities/items, not people. A published status alone also
does not prove the participation deadline is still in the future.

Public JavaScript at `/kppp/eproc-auction-management/main.js` references:

```text
GET /auction-service/v1/api/e-auction/{noticeId}/auction-participants
```

The client method is named `getEvaluateSuppliers`, so this is an evaluation workflow reference, not proof
that ordinary bidders can see registrations before closing.

Public JavaScript at `/kppp/eproc-auction-partcipation/main.js` references:

```text
GET /live-auction-service/v1/api/live-auction/{noticeId}/auction/{lotOrItemId}/last-five-bidders-with-amount
GET /live-auction-service/v1/api/live-auction/{noticeId}/auction/{lotOrItemId}/get-past-bidder-list?pageIndex={page}&pageSize={size}
GET /live-auction-service/v1/api/live-auction/{noticeId}/auction/{lotOrItemId}/get-past-bidder-ranks?pageIndex={page}&pageSize={size}
```

These are **source-discovered, not response-verified**. The last-five list cannot establish a total count
or all registered participants. Do not change these distinct APIs' `pageSize` parameter based on the
public search finding; their contracts have not been tested. The existing signed-in collector also
references department-user ranks and per-supplier bid histories; those were not called here.

To investigate further, the account owner should sign in normally and open an auction they may access.
Inspect only read-only data actually available to that account. Establish whether records represent EOI
submissions, eligible/paid participants, or people who bid; inspect pagination before reporting a total.
Publish aggregate counts only after those semantics and permissions are verified. Do not copy credentials,
personal identities, stable bidder identifiers or unsanitized HAR files into this repo. Do not submit bids,
participation, payments or account changes as part of data inspection.

## 6. Other Findings and Follow-Up Work

1. **Historical price joins:** `export_lots_csv.py` keys archived final prices by `(group, site)` and
   attaches them to eligible statuses without an auction-round key. A historical price can therefore be
   attributed to another re-listing. Use notice/lot IDs or an evidence-backed round/date match. Not fixed here.
2. **Metrics conflict:** homepage `/metrics/get-count` reported 24 live auctions, 23 ending today and
   3,930 live tenders. `/metrics/get-portal-metrics` reported 0, 0 and 2 respectively. The ending-today
   search header reported 71 with the tested body. Reconcile freshness, dates and semantics before using these counters.
3. **Announcements:** a BDA rescheduling message is available publicly. Match announcements to their
   affected rounds; an old portal message must not override an unrelated lot's current dates.
4. **Units and identity:** classify property versus non-property; use official specifications for area.
   Stable item-code behavior across re-listings was not established. Match locality/block, site, dimensions
   and source evidence, not site number alone.
5. **Uncertainty:** preserve raw times and source IDs. Portal date strings lack a timezone suffix;
   interpret wall-clock time as Asia/Kolkata after checking server time, separately from epoch timestamps.
6. **Ingestion:** prefer offline/server-side collection and sanitized static exports. Vercel-origin CORS
   was not tested. Cache large/shared documents, collect changed records selectively, and seek permission
   before sustained production harvesting. Public access is not a redistribution license or SLA.

The client inventory also references tender search/detail/document/addendum/corrigendum routes, tender
commercial comparisons, department lookups, debarment evidence and account workflows. Their exact
expressions are recorded, but successful/public access was not established for all of them. No runtime
models, pricing logic, bidder scraping or deployed site data were changed by this PR.

## Reproduce and Validate

From the repository root in Windows PowerShell 5.1:

```powershell
& .\pipeline\tools\collect_kppp_public.ps1 -NoticeIds 29761,19567,1095,25447 -ExportBdaIndex -DiscoverClient -PortalSnapshot
& .\pipeline\tools\test_collect_kppp_public.ps1
```

For only Site 303's two rounds, run the collector without switches. `-CountBdaStatuses` requests one row
per status; `-ExportBdaIndex` uses sequential 100-row pages. Detail requests are limited to supplied notice
IDs. Optional client discovery reads only three public bundles; chunk names can change.

Output goes to a new timestamped directory in ignored `pipeline/tools/kppp-public-evidence/`. It includes
raw request evidence, auction detail, optional index JSON/CSV and optional client references. Any request
failure stops collection; errors remain in the request log rather than becoming empty auction results.
The collector has a 30-second request timeout, no automatic retry, 200-page safety limit per status, and
checks for changed totals, duplicate IDs and short pages. Stop and retry later when a changing snapshot
prevents completeness; do not bypass access or rate controls.

The complete original snapshot passed unique-ID/total-count checks and exact CSV overlap checks. A fresh
repo-collector run passed 23 public requests across lot-wise/item-wise details, corrigenda and status
queries. Offline tests exercise pagination and failure handling without making network requests. Snapshot
collection is not atomic and future counts/fields may differ. Live winning prices, complete pre-close
participant counts, role permissions, PDF minimum-bid terms and browser CORS remain unverified.