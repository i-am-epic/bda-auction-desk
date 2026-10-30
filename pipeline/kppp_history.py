"""Past BDA auctions on KPPP: every lot for our layouts with its outcome status, base rate (Rs/sq m) and bid date.
KPPP does not publish winning bids, but it does show which lots sold (Finalized) and which drew nobody (No Participations / No Bids),
and the base rate BDA set each time -> base-price growth per layout and repeat-unsold sites."""
import json, sys, subprocess, time
from concurrent.futures import ThreadPoolExecutor
API = 'https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service'
WORDS = ['BANASHANKARI', 'ANJANAPURA', 'ARKAVATHI', 'ARKAVATHY', 'VISHWESHWARAIAH', 'J P NAGAR', 'JP NAGAR',
         'KUMARASWAMY', 'BTM', 'NGEF']
STATUSES = ['FINALIZED', 'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED', 'BIDDING_CLOSED', 'EVALUATED', 'UNDER_EVALUATION', 'CANCELLED']
NL = chr(10)

def curl(args, data=None):
    r = subprocess.run(['curl', '-s', '-m', '90', '-D', '-'] + args, capture_output=True, text=True, encoding='utf8', input=data)
    head, _, body = r.stdout.partition(NL + NL)
    total = next((int(l.split(':')[1]) for l in head.splitlines() if l.lower().startswith('x-total-count')), 0)
    return body, total

def search(st, w, page):
    body, total = curl(['-X', 'POST', f'{API}/search/auction-search?page={page}&pageSize=10', '-H', 'Content-Type: application/json',
                        '-d', json.dumps({'auctionStatus': st, 'auctionTitle': w})])
    try: return json.loads(body or '[]'), total
    except Exception: return [], total

lots = {}
for st in STATUSES:
    for w in WORDS:
        rows, total = search(st, w, 0)
        pages = [rows] + list(ThreadPoolExecutor(6).map(lambda p: search(st, w, p)[0], range(1, (total + 9)//10)))
        for rs in pages:
            for a in rs:
                if a['auctionNoticeNumber'].startswith('BDA/'):
                    a['statusKey'] = st; lots[a['auctionNoticeId']] = a
        print(st, w, total, len(lots), flush=True)

def detail(a):
    for _ in range(3):
        body, _t = curl([f"{API}/{a['auctionNoticeId']}/view-auction"])
        try:
            d = json.loads(body)
            slot = (d.get('auctionBiddingSlotDTO') or [{}])[0]
            n = d['auctionNoticeDTO']
            sch = ((d.get('auctionScheduleInformationDTO') or {}).get('auctionSchedule') or {})
            rec = d.get('recallAuctionDTO') or {}
            a['baseRate'] = float(n.get('totalAmount') or 0)
            a['bidDate'] = slot.get('auctionStartDate')
            # everything else KPPP shows publicly for a lot (bidders and bid amounts are login-only)
            a.update(bidEnd=slot.get('auctionEndDate'), deltaMin=slot.get('deltaTime'), eoiDeadline=sch.get('auctionParticipationInterestDate'),
                     emd=float(sch.get('fullEmd') or 0) or None, fee=float(sch.get('auctionFee') or 0) or None,
                     dept=n.get('deptName'), publishedBy=n.get('auctionPublishedByPost'),
                     showsLastBid=n.get('displayLastAcceptedBidAmountYn'), showsBidders=n.get('displayBiddersListYn'),
                     recallReason=(rec.get('recallReasonOthers') or rec.get('recallReason')) if rec else None,
                     recalledOn=time.strftime('%d-%m-%Y', time.localtime(rec['recalledDate'] / 1000)) if rec.get('recalledDate') else None)
            return a
        except Exception:
            time.sleep(2)
    return a

out = list(ThreadPoolExecutor(8).map(detail, lots.values()))
json.dump(out, open(sys.argv[1], 'w', encoding='utf8'), ensure_ascii=False)
print('lots', len(out))
