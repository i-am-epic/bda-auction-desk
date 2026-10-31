# KPPP API — public endpoints reference

The Karnataka Public Procurement Portal (kppp.karnataka.gov.in) is an Angular app that reads from a REST API.
These are the **public** endpoints (no login, no personal data) used by this project's pipeline to build base
rates, outcomes and bidding history. They need no token and return no bidder identities.

Base: `https://kppp.karnataka.gov.in`

## 1. Search auctions by status (+ optional keyword / notice number)
`POST /supplier-registration-service/v1/api/portal-service/search/auction-search?page=0&pageSize=10`

```bash
curl -s -X POST "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/search/auction-search?page=0&pageSize=10" \
  -H "Content-Type: application/json" \
  -d '{"auctionStatus":"FINALIZED","auctionTitle":"Banashankari"}'
```
- `auctionStatus` is **required**. One of:
  `PUBLISHED, LIVE_AUCTION, BIDDING_CLOSED, NO_PARTICIPATIONS, NO_BIDS_RECEIVED, CANCELLED, UNDER_EVALUATION, EVALUATED, FINALIZED`.
- Optional filters: `auctionTitle` (keyword), `auctionNoticeNumber` (exact, e.g. `BDA/2026-27/AUCTION4036`).
- Returns up to `pageSize`; total count is in the `X-Total-Count` response header. Page with `page=0,1,2,…`.
- Each row has `auctionNoticeId` (the numeric id used below), `auctionNoticeNumber`, `auctionTitle`, `auctionStatus`, `auctionPublishedDate`.

## 2. Auction detail — base rate, reserve, dates, status
`GET /supplier-registration-service/v1/api/portal-service/{noticeId}/view-auction`

```bash
curl -s "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/29695/view-auction"
```
- `auctionNoticeDTO.totalAmount` = base price in Rs/sq.m.
- `auctionBiddingSlotDTO[0]` = bidding start/end + delta (extension) minutes.
- `auctionScheduleInformationDTO.auctionSchedule` = EOI deadline (`auctionParticipationInterestDate`), EMD (`fullEmd`), fee (`auctionFee`).
- `recallAuctionDTO` = cancellation reason + date, when cancelled.

## 3. Documents attached to a lot
`GET /supplier-registration-service/v1/api/portal-service/{noticeId}/auction-documents`

```bash
curl -s "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/29695/auction-documents"
```

## Notes
- No `Authorization` header needed for the three above.
- The pipeline (`kppp.py`, `kppp_history.py`) uses exactly these to collect lot status, base rate and bid date.

## Finding other endpoints yourself
Everything the app can do is reachable from its own code and your own session:
1. Sign in, press F12 → **Network** tab → filter **Fetch/XHR**, tick **Preserve log**.
2. Click through the app; each row is one API call — select it to see method, URL, request and response.
3. Authenticated calls carry an `Authorization: Bearer …` header (copy it from any such row to replay a call).

This file deliberately stops at the public, non-PII, read-only surface. The authenticated endpoints that return
other bidders' identities, and any write/payment endpoints (placing bids, paying EMD/fee), are not catalogued here —
discover and test those in your own Network tab, with your own account, at your own discretion.
