"""BDA e-auction — Nadaprabhu Kempegowda Layout (NPKL), notice dated 03.11.2026.
Rows + geotag auto-extracted by fetch_bda.py from the BDA geotag map (http://106.51.29.213:9005/) joined to KPPP.
NPKL is a provisional market entry (see market.py) using the shared model for now; a layout-specific model comes later."""

AUCTION = dict(
    id='npkl', code='NPKL', title='BDA e-auction — Nadaprabhu Kempegowda Layout', notice='BDA/EM/e-Auction/NPKL/2026-27', noticeDate='2026-11-03',
    eoiDeadline='2026-11-16T17:00:00+05:30', status='bidding',
    bidDays=[{'date': '2026-11-17', 'range': 'Sl 1-25'}, {'date': '2026-11-18', 'range': 'Sl 26-50'}, {'date': '2026-11-19', 'range': 'Sl 51-75'}, {'date': '2026-11-20', 'range': 'Sl 76-101'}],
    slots=[(1, 25, '2026-11-17'), (26, 50, '2026-11-18'), (51, 75, '2026-11-19'), (76, 101, '2026-11-20')],
    emd=400000, fee=500, minBidUplift=0.10,
    notice_pdf='https://www.bdakarnataka.in/api/media/e-auction/pdf_press_release/BDA-Auction_-_English_1793698767847_1a803e54.pdf',
    corrigendum_pdf='', geotag_url='http://106.51.29.213:9005/',
    kppp='https://kppp.karnataka.gov.in/#/portal/Auctions/live', helpline='9483166622',
    corrections={},
)

ROWS = """
51|B1-SK-769|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|12|8.8|105.6|80000|South|NPKL
57|B1-SJ-1988|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|12|18|216.0|80000|South|NPKL
56|B1-SJ-1824|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|18|12|216.0|80000|South|NPKL
52|B1-SK-87|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|9|6|54.0|80000|South|NPKL
53|B1-SK-88|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|9|6|54.0|80000|South|NPKL
48|B1-SK-737|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|12|8.8|105.6|80000|South|NPKL
50|B1-SK-39|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|12|(8.40+8.50)/2|101.4|80000|South|NPKL
54|B1-SJ-1749/E|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|12|8.9|106.8|80000|South|NPKL
55|B1-SJ-1749/F|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|12|8.9|106.8|80000|South|NPKL
49|B1-SK-38|Nadaprabhu Kempegowda Layout, Kodigehalli 1st Block|(8.10+11.90)/2|(17.60+17.10)/2|173.5|80000|South|NPKL
97|B2-SC-3079|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(8.20+9.60)/2|106.8|80000|South|NPKL
96|B2-SC-3105|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(12.20+13.80)/2|156.0|80000|South|NPKL
95|B2-SC-3128|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(14.90+16.30)/2|187.2|80000|South|NPKL
94|B2-SC-3129|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(7.40+9.00)/2|98.4|80000|South|NPKL
93|B2-SC-3154|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(10.10+11.50)/2|129.6|80000|South|NPKL
92|B2-SC-3155|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(11.50+13.10)/2|147.6|80000|South|NPKL
99|B2-SC-3116|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(16.80+15.70)/2|195.0|80000|South|NPKL
100|B2-SC-3092|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(8.90+7.80)/2|100.2|80000|South|NPKL
98|B2-SC-3117|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|12|(14.80+13.70)/2|171.0|80000|South|NPKL
101|B2-SC-3070|Nadaprabhu Kempegowda Layout, Kannalli, Block 2|18|(11.40+13.90)/2|227.7|80000|South|NPKL
84|B3-SF-2007|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(8.8+8.00)/2|12|100.8|80000|South|NPKL
83|B3-SF-2042|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(8.0+7.60)/2|12|93.6|80000|South|NPKL
90|B3-SF-1888|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(9.30+9.80)/2|12|114.6|80000|South|NPKL
91|B3-SF-1854|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(8.80+9.30)/2|12|108.6|80000|South|NPKL
88|B3-SF-1936|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(9.3+9.8)/2|12|114.6|80000|South|NPKL
89|B3-SF-1901|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(8.8+9.3)/2|12|108.6|80000|South|NPKL
86|B3-SF-1989|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(9.3+9.8)/2|12|114.6|80000|South|NPKL
87|B3-SF-1954|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(8.8+9.3)/2|12|108.6|80000|South|NPKL
85|B3-SF-2006|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(8.80+9.30)/2|12|108.6|80000|South|NPKL
82|B3-SE-1688|Nadaprabhu Kempegowda Layout, Ramsandra, Block 3|(18.60+19.00)/2|24|451.2|80000|South|NPKL
24|B4-SD-1885|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|14.6|12|175.2|80000|South|NPKL
23|B4-SD-1884|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|14.6|12|175.2|80000|South|NPKL
15|B4-SD-1861|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|14.6|12|175.2|80000|South|NPKL
16|B4-SD-1860|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|14.6|12|175.2|80000|South|NPKL
17|B4-SD-1789|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|14.6|12|175.2|80000|South|NPKL
22|B4-SA-128|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|6|9|54.0|80000|South|NPKL
21|B4-SA-129|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|6|9|54.0|80000|South|NPKL
19|B4-SA-164|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|9|12|108.0|80000|South|NPKL
18|B4-SA-165|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|9|13.7|123.3|80000|South|NPKL
20|B4-SA-340|Nadaprabhu Kempegowda Layout, Kommaghatta 4th Block|9|11.55|103.95|80000|South|NPKL
1|B5-SG-6247|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|12|(16.30+14.00)/2|181.8|80000|South|NPKL
74|B6-SH-3274|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|24|(24.10+20.80)/2|538.8|80000|South|NPKL
75|B6-SH-3273|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|18|(18.30+20.80)/2|351.9|80000|South|NPKL
72|B6-SH-3540|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|(9.80+12.30)/2|18|198.9|80000|South|NPKL
73|B6-SH-3494|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|8.9|12|106.8|80000|South|NPKL
76|B6-SH-3518|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|11.9|18|214.2|80000|South|NPKL
77|B6-SH-3517|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|11.9|12|142.8|80000|South|NPKL
81|B6-SB-470|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|(18.30+17.70)/2|18|324.0|80000|South|NPKL
80|B6-SB-512|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|(11.30+11.70)/2|12|138.0|80000|South|NPKL
79|B6-SB-515|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|(10.90+10.40)/2|12|127.8|80000|South|NPKL
78|B6-SB-564|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|(9.70+9.20)/2|12|113.4|80000|South|NPKL
70|B6-SJ-4719|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|9|(10.00+9.70)/2|88.65|80000|South|NPKL
69|B6-SJ-4720/I|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|9|(9.00+9.70)/2|84.15|80000|South|NPKL
71|B6-SJ-4718/N|Nadaprabhu Kempegowda Layout, Bheemanakuppe, Block 6|9|(10.20+10.40)/2|92.7|80000|South|NPKL
26|B7-SA-249|Nadaprabhu Kempegowda Layout, Kommaghatta 7th Block|18|(7.80+12.20)/2|180.0|80000|South|NPKL
25|B7-SA-211|Nadaprabhu Kempegowda Layout, Kommaghatta 7th Block|15|(9.15+13.33)/2|168.37|80000|South|NPKL
27|B7-SA-250|Nadaprabhu Kempegowda Layout, Kommaghatta 7th Block|18|(11.80+16.00)/2|250.2|80000|South|NPKL
67|B7-SF-6325|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|(18.10+17.50)/2|18|320.4|80000|South|NPKL
65|B7-SF-6294|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|(18.50+18.10)/2|12|219.6|80000|South|NPKL
68|B7-SL-4406|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|8.8|12|105.6|80000|South|NPKL
66|B7-SF-6311/W|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|(16.50+15.80)/2|18|290.7|80000|South|NPKL
63|B7-SH-3745|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|(16.00+16.40)/2|12|194.4|80000|South|NPKL
64|B7-SH-3765|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|(12.60+12.10)/2|12|148.2|80000|South|NPKL
59|B7-SG-3371|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|18|(15.20+15.40)/2|275.4|80000|South|NPKL
58|B7-SG-3346|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|18|(15.30+15.20)/2|274.5|80000|South|NPKL
62|B7-SG-3407|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|12|(12.60+12.50)/2|150.6|80000|South|NPKL
61|B7-SG-3406|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|12|(12.50+12.60)/2|150.6|80000|South|NPKL
60|B7-SG-3372|Nadaprabhu Kempegowda Layout, Bheemanakuppe 7th Block|12|(11.90+11.80)/2|142.2|80000|South|NPKL
36|B8-SF-2036|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
28|B8-SF-2037|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
34|B8-SF-2005|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
35|B8-SF-2006|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
32|B8-SF-1976|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
33|B8-SF-1977|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
31|B8-SF-1951|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|9|12|108.0|80000|South|NPKL
30|B8-SD-1490|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|(14.00+17.40)/2|12|200.4|80000|South|NPKL
37|B8-SD-1470||(12.00+13.40)/2|12|152.4|80000|South|NPKL
29|B8-SD-1471|Nadaprabhu Kempegowda Layout, Sulikere 8th Block|(13.40+14.50)/2|12|167.4|80000|South|NPKL
47|B9-SC-2017|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|18|21.2|381.6|80000|South|NPKL
41|B9-SA-355|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|(6.50+5.20)/2|9|52.7|80000|South|NPKL
40|B9-SA-354|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|(7.60+6.50)/2|9|63.5|80000|South|NPKL
39|B9-SA-315|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|(10.70+8.50)/2|9|86.4|80000|South|NPKL
42|B9-SA-155|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|18|11.8|212.4|80000|South|NPKL
43|B9-SA-156|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|18|11.8|212.4|80000|South|NPKL
38|B9-SA-73|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|11.8|18|212.4|80000|South|NPKL
44|B9-SC-1903|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|16.8|24|403.2|80000|South|NPKL
45|B9-SC-2003|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|18|11.8|212.4|80000|South|NPKL
46|B9-SC-2016|Nadaprabhu Kempegowda Layout,Kenchanapura 9th Block|(18.00+17.80)/2|15.5|277.45|80000|South|NPKL
13|B5-SG-6201|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|18|(14.35+17.65)/2|288.0|80000|South|NPKL
3|B5-SG-6213|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|18|(10.30+13.60)/2|215.1|80000|South|NPKL
14|B5-SF-1642||12|(17.60+13.80)/2|188.4|80000|South|NPKL
9|B5-SG-5955|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|(10.20+9.80)/2|12|120.0|80000|South|NPKL
10|B5-SG-6093|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|12|11.8|141.6|80000|South|NPKL
7|B5-SG-6075|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|8.9|9|80.1|80000|South|NPKL
8|B5-SG-6074|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|8.9|9|80.1|80000|South|NPKL
4|B5-SG-6212|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|12|(11.20+8.80)/2|120.0|80000|South|NPKL
6|B5-SG-6183|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|18|(17.30+20.70)/2|342.0|80000|South|NPKL
5|B5-SG-6200|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|18|(12.10+8.70)/2|187.2|80000|South|NPKL
11|B5-SG-2278|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|(10.70+16.20)/2|12|161.4|80000|South|NPKL
12|B5-SG-2302|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|(7.75+11.80)/2|9|87.97|80000|South|NPKL
2|B5-SG-6228|Nadaprabhu Kempegowda Layout, K Krishnasagara 5th Block|12|(14.00+11.80)/2|154.8|80000|South|NPKL
"""
WITHDRAWN = set()
LOCALITY = {}
