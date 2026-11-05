# KPPP API — public endpoints reference

The Karnataka Public Procurement Portal (kppp.karnataka.gov.in) is an Angular app that reads from a REST API.
The routes below were checked without login on **4 November 2026**. Public responses can include official
contact/publishing metadata; publish a selected field allowlist, not raw responses. No bidder identities,
credentials, bid submissions or payments were collected during these checks.

Base: `https://kppp.karnataka.gov.in`

## 1. Search auctions by status (+ optional keyword / notice number)
`POST /supplier-registration-service/v1/api/portal-service/search/auction-search?page=0&size=100`

```bash
curl -s -X POST "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/search/auction-search?page=0&size=100" \
  -H "Content-Type: application/json" \
  -d '{"auctionStatus":"FINALIZED","departmentId":1566}'
```
- `auctionStatus` is **required**. One of:
  `PUBLISHED, LIVE_AUCTION, BIDDING_CLOSED, NO_PARTICIPATIONS, NO_BIDS_RECEIVED, CANCELLED, UNDER_EVALUATION, EVALUATED, FINALIZED`.
- Optional filters: `departmentId` (**1566 = BDA**), `auctionTitle` (keyword), `auctionNoticeNumber` (exact).
- Use **`size`**, not `pageSize`. Tests with `pageSize=25` returned 10 rows, while `size=25` returned all 24 live notices in that snapshot.
- Read the total count from `X-Total-Count`; paginate with `page=0,1,2,...`, deduplicate notice IDs and check completeness.
- The existing history script steps through pages of 10, so the ignored `pageSize=10` parameter alone does not establish missing pages. Increasing it without changing to `size` would be unsafe.
- `auctionNoticeNumber: "BDA"` returned no matches; it is not a verified prefix filter.
- Each row has `auctionNoticeId` (the numeric id used below), `auctionNoticeNumber`, `auctionTitle`, `auctionStatus`, `auctionPublishedDate`.
- Search statuses are display strings such as `"Bidding Closed"`; detail statuses are enums such as `"BIDDING_CLOSED"`. Preserve a canonical status key.
- The UI also references date-range and inviting-strategy filters, but their serialization and combinations were not independently verified.

## 2. Auction detail — base rate, reserve, dates, status
`GET /supplier-registration-service/v1/api/portal-service/{noticeId}/view-auction`

```bash
curl -s "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/29695/view-auction"
```
- `auctionNoticeDTO.totalAmount` is not universally a plot price or Rs/sq.m. Check the item units, specifications and notice terms. A BDA fixed-deposit auction uses percentages.
- Iterate **every** entry in `auctionBiddingSlotDTO`: bidding start/end, slot ID and delta (extension) minutes. These dates are scheduled dates, not necessarily the final extended close.
- `auctionNoticeDTO.itemGroupType` determines whether to request lots (`LOT_WISE`) or slot items (`ITEM_WISE`).
- `auctionScheduleInformationDTO.auctionSchedule` = EOI deadline (`auctionParticipationInterestDate`), EMD (`fullEmd`), fee (`auctionFee`).
- `recallAuctionDTO` = cancellation reason + date, when cancelled.
- `FINALIZED` does not establish a completed sale. The finalized previous Site 303 round returns `soldYn: null` at lot level.
- `displayBiddersListYn` and `displayLastAcceptedBidAmountYn` are display settings, not counts or bid amounts. Public live-auction detail/lot samples did not expose a participant count.

## 3. Documents attached to a lot
`GET /supplier-registration-service/v1/api/portal-service/{noticeId}/auction-documents`

```bash
curl -s "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/29695/auction-documents"
```

The list provides document names, UUIDs, MIME types and timestamps. Download using
`GET /supplier-registration-service/v1/api/portal-service/{noticeId}/auction-document/{uuid}`.
The response can be `application/octet-stream`; inspect file metadata and signature. The tested Site 303
notice PDF is approximately 24 MB. Cache and deduplicate downloads. Its substantive minimum-bid clause
was not verified by the available text extractor.

## 4. Lot and item details

All paths below are relative to `/supplier-registration-service/v1/api/portal-service`.
Use IDs returned by parent responses; printed auction numbers, slot IDs, lot IDs and item IDs are different identifiers.

| Method | Path | Purpose |
|---|---|---|
| GET | `/{noticeId}/bidding-slot/{slotId}/get-all-lots` | Lot initial/reserve price, increment, extended end time, status, force-close fields and nested items. |
| GET | `/{noticeId}/slot/{slotId}/get-all-items` | Item-wise auction equivalent. Returns HTTP 400 for a lot-wise notice. |
| GET | `/{noticeId}/lot/{lotId}/get-all-items` | Item code, name, specifications, units, quantity and price within a lot. |

Verified examples: notice `29761`, slot `33220`, lot `38995` for Site 303; notice `25447`, slot `27808` for an item-wise auction.
Site 303 has a 90 m2 specification but `quantity: "1.0000"` and `netAmount: "84000.00"`. Neither quantity nor
net amount represents its plot area or whole-plot price. Keep API reserve, notice-defined minimum valid bid,
initial unit price and whole-plot amount separate.

## 5. Corrigenda and cancellation documents

| Method | Path | Purpose |
|---|---|---|
| GET | `/{noticeId}/get-recall-auction-documents` | Recall attachment metadata. Notice 1095 has a system-saved JSON attachment reference. |
| GET | `/{noticeId}/auction-corrigendum` | Corrigenda list. Notice 25447 has IDs 1071 and 1072. |
| GET | `/{noticeId}/auction-corrigendum/{corrigendumId}/get-auction-corrigendum` | Original/revised deadlines, slot dates, reasons and approval status. |
| GET | `/{noticeId}/auction-corrigendum/{corrigendumId}/get-auction-corrigendum-files` | Corrigendum file metadata and UUIDs. |
| GET | `/{noticeId}/auction-corrigendum/{corrigendumId}/auction-corrigendum-file/uuid/{uuid}/auction-download-file` | Corrigendum binary download. A DOCX signature was verified. |

## 6. Supporting public endpoints

| Method | Path | Purpose / qualification |
|---|---|---|
| POST | `/search/auctions-ending-today?page=0&size=100` | Closing-today search; tested with `{"auctionStatus":"LIVE_AUCTION"}`. Its count did not match homepage metrics. |
| GET | `/departments/activeDepartment` | Department directory; the array is inside `responseObject`. |
| GET | `/departments/activeLocation/{departmentId}` | Procuring-entity location lookup, not parcel coordinates. BDA returned an empty array. |
| GET | `/get-current-time` | Server epoch milliseconds and formatted portal time. |
| GET | `/metrics/get-count` | Homepage metrics feed. Portal-wide, not BDA-only. |
| GET | `/metrics/get-portal-metrics` | Alternative metrics; disagreed sharply with the homepage feed. Freshness/semantics unverified. |
| GET | `/ANNOUNCEMENTS/get-portal-announcements` | Announcements, including a BDA rescheduling message. Match messages to their affected round. |
| GET | `/EVENTS/get-portal-announcements` | Other homepage notification feed. |

## Access and scope

These 20 endpoint templates returned successful responses without Authorization headers or session cookies
in the checked samples. That does not guarantee future access, an unrestricted redistribution license, or
that all records share the same permissions. The existing history collector uses search/detail calls; it
does not yet ingest all the lot/item and corrigendum data documented here.

Use sequential, cached collection; stop on access/rate errors. Respect CAPTCHA and role boundaries.
Date strings have no timezone suffix: retain raw values and interpret portal wall-clock time as
Asia/Kolkata after checking server time. Cross-origin access from the deployed website was not tested;
prefer offline/server-side ingestion and sanitized static exports.

For authenticated investigation, sign in normally and inspect only requests/data your account is entitled
to access. Do not share passwords, OTPs, tokens, cookies, or unsanitized HAR files. A client-code reference
is not proof of permission, and even some GET routes change state. No private bidder-data or write/payment
routes were called during the public investigation. No exhaustive backend/OpenAPI inventory is claimed.
