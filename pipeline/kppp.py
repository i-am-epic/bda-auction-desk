"""Find each BDA site's lot on the Karnataka Public Procurement Portal (KPPP) by title search.
Usage: python kppp.py <out.json> <STATUS> [STATUS ...]   e.g. PUBLISHED, or FINALIZED BIDDING_CLOSED for past auctions."""
import json, sys, time, subprocess
API = 'https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service'
WORDS = ['BANASHANKARI', 'ANJANAPURA', 'ARKAVATHI', 'ARKAVATHY', 'VISHWESHWARAIAH', 'VISVESVARAYA', 'VISHVESHWARAH',
         'J P NAGAR', 'JP NAGAR', 'KUMARASWAMY', 'BTM', 'NGEF', 'BANASAWADI', 'HSR', 'HBR', 'KEMPEGOWDA', 'SHIVARAM']
NL = chr(10)

def post(path, body):
    # curl, because KPPP serves an incomplete TLS chain that Python's ssl module rejects
    r = subprocess.run(['curl', '-s', '-m', '90', '-D', '-', '-X', 'POST', API + path, '-H', 'Content-Type: application/json',
                        '-d', json.dumps(body)], capture_output=True, text=True, encoding='utf8')
    head, _, body_txt = r.stdout.partition(NL + NL)
    total = next((int(l.split(':')[1]) for l in head.splitlines() if l.lower().startswith('x-total-count')), 0)
    return json.loads(body_txt or '[]'), total

out, statuses = sys.argv[1], sys.argv[2:]
found = {}
for st in statuses:
    for w in WORDS:
        page = 0
        while True:
            rows, total = post(f'/search/auction-search?page={page}&pageSize=10', {'auctionStatus': st, 'auctionTitle': w})
            for a in rows:
                if a['auctionNoticeNumber'].startswith('BDA/'):
                    found[a['auctionNoticeId']] = a
            page += 1
            if page*10 >= total or not rows: break
            time.sleep(0.2)
        print(st, w, total, len(found), flush=True)
json.dump(list(found.values()), open(out, 'w', encoding='utf8'), ensure_ascii=False)
