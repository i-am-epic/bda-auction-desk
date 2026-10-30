"""BDA e-auction T-15/2026-27 (notice dated 03.10.2026) + corrigendum 1574.
ROWS transcribed from the notice PDF. Fields: sl | site | layout | EW | NS | area_sqm | base_rate_per_sqm | zone | locality group.
Rows starting with C are sites added by the corrigendum."""

AUCTION = dict(
    id='t15', code='T-15', title='BDA e-auction T-15/2026-27', notice='BDA/EM/e-Auction/T-15/2026-27', noticeDate='2026-10-03',
    eoiDeadline='2026-10-31T17:00:00+05:30', status='bidding',
    bidDays=[dict(date='2026-11-02', range='Sl 1-46'), dict(date='2026-11-03', range='Sl 47-92'), dict(date='2026-11-04', range='Sl 93-138')],
    slots=[(1, 46, '2026-11-02'), (47, 92, '2026-11-03'), (93, 138, '2026-11-04')],
    emd=400000, fee=500, minBidUplift=0.10,
    notice_pdf='https://www.bdakarnataka.in/api/media/e-auction/pdf_press_release/e_auction-12102026_1791186164533_0e517992.pdf',
    corrigendum_pdf='https://www.bdakarnataka.in/api/media/e-auction/pdf_press_release/1574_BDA_corrigendum_(1)-1_1792750776940_04ea4c26.pdf',
    geotag_url='http://106.51.29.213/', kppp='https://kppp.karnataka.gov.in/#/portal/Auctions/live', helpline='9483166622',
    corrections={'77': 233.98},   # corrigendum area changes, sl -> new area in m2
)

ROWS = """
1|711|Anjanapura Township, 1st Block, Anjanapura|[7.50+3.10]/2|12.00|63.60|73000|South|ANJ
2|593|Anjanapura Township, 1st Block, Anjanapura|[9.00+3.70]/2|12.00|76.20|73000|South|ANJ
3|178|Anjanapura Township, 4th Block, Anjanapura|11.00|12.00|132.00|73000|South|ANJ
4|365|Anjanapura Township, 5th Block, Anjanapura|12.00|[13.00+17.70]/2|184.20|73000|South|ANJ
5|416/A|Anjanapura Township, 6th Block, Anjanapura|12.00|[12.00+10.00]/2|132.00|71000|South|ANJ
6|458|Anjanapura Township, 6th Block, Anjanapura|12.00|[10.50+8.60]/2|114.60|71000|South|ANJ
7|552|Anjanapura Township, 6th Block, Anjanapura|[10.00+10.50]/2|12.00|123.00|71000|South|ANJ
8|553|Anjanapura Township, 6th Block, Anjanapura|[10.00+10.50]/2|12.00|123.00|71000|South|ANJ
9|1150|Anjanapura Township, 8th Block, Anjanapura|(8.30+3.00)/2|12.00|67.80|80000|South|ANJ
10|750/D|Anjanapura Township, 8th Block, Anjanapura|[4.90+22.30]/2|18.00|244.80|80000|South|ANJ
11|749/D|Anjanapura Township, 8th Block, Anjanapura|[1/2*21.60]|24.00|259.20|80000|South|ANJ
12|1373|Banashankari 6th Stage, 7th Block, Sompura|12|(15.00+28.00)/2|258.00|73000|South|BSK6O
13|303|Banashankari 6th Stage, 11th Block, Ganakallu|[4.50+10.50]/2|12.00|90.00|84000|South|BSK6O
14|227|Banashankari 6th Stage, 11th Block, Ganakallu|24|(14.10+14.80)/2|346.80|84000|South|BSK6O
15|963|Banashankari 6th Stage, 11th Block, Ganakallu|12.00|12.00|144.00|84000|South|BSK6O
16|676|Banashankari 6th Stage, 1st Block, Turahalli|12.50|[21.50+19.00]/2|253.12|73000|South|BSK6T
17|121|Banashankari 6th Stage, 1st Block, Turahalli|18.00|[5.50+11.00]/2|148.50|73000|South|BSK6T
18|1234|Banashankari 6th Stage, 2nd Block, Turahalli|12.00|(9.00+8.00)/2|102.00|73000|South|BSK6T
19|1860|Banashankari 6th Stage, 3rd Block, Hemmigepura|[16.00+4.90]/2|12.00|125.40|75000|South|BSK6M
20|2393|Banashankari 6th Stage, 3rd Block, Hemmigepura|24|(15.25+15.00)/2|363.00|75000|South|BSK6M
21|255/M|Banashankari 6th Stage, 3rd Block, Lingadeeranahalli|12|(5.00+2.00)/2|42.00|75000|South|BSK6M
22|1/A|Banashankari 6th Stage, 3rd Block, Lingadeeranahalli|1.5|18|27.00|75000|South|BSK6M
23|255/L|Banashankari 6th Stage, 3rd Block, Lingadeeranahalli|18|(0.50*3.50)/2|31.50|75000|South|BSK6M
24|1632|Banashankari 6th Stage, 4th Block, Lingadeeranahalli|[11.80+24.30]/2|18.00|324.90|70000|South|BSK6M
25|1704|Banashankari 6th Stage, 4th Block, Lingadeeranahalli|[9.00+12.00]/2|12.00|126.00|70000|South|BSK6M
26|1105|Banashankari 6th Stage, 5th Block, Hemmigepura|12.00|[9.45+11.00]/2|122.70|72000|South|BSK6M
27|1129|Banashankari 6th Stage, 5th Block, Hemmigepura|12.00|[18.80+11.40]/2|181.20|72000|South|BSK6M
28|1640/25|Banashankari 6th Stage, 5th Block, Hemmigepura|18.00|12.00|216.00|72000|South|BSK6M
29|1710|Banashankari 6th Stage, 5th Block, Lingadeeranahalli|[23.00+5.00]/2|24.00|336.00|72000|South|BSK6M
30|1690|Banashankari 6th Stage, 5th Block, Lingadeeranahalli|[7.50+21.00]/2|18.00|256.00|72000|South|BSK6M
31|1675|Banashankari 6th Stage, 7th Block, Sompura|12.00|[26.00+27.50]/2|321.00|73000|South|BSK6O
32|1588|Banashankari 6th Stage, 7th Block, Sompura|18.00|[16.00+17.00]/2|297.00|73000|South|BSK6O
33|776|Banashankari 6th Stage, 9th Block, Hemmigepura|(16.00+12.00)/2|24.00|336.00|74000|South|BSK6N
34|1246|BTM 4th Stage, 2nd Block, Devarachikkanahalli|21.00|12.20|256.20|84000|South|BTM4
35|51|BTM 6th Stage, 1st Phase, Hulimavu|12.00|[8.50+6.00]/2|87.00|90000|South|BTM6
36|1056|FE of Anjanapura 10th Block, Gollahalli|18.00|(27+22)/2|441.00|84000|South|FEANJ
37|838|FE of Anjanapura 11th Block, Kembathalli|12.00|(6.00+14.00)/2|120.00|70000|South|FEANJ
38|1143|FE of Anjanapura 11th Block, Kembathalli|18.00|(18.20+11.00)/2|262.80|70000|South|FEANJ
39|1048|FE of Anjanapura 9th Block, Gollahalli|9.00|4.60|41.40|70000|South|FEANJ
40|1069|FE of Anjanapura 9th Block, Gollahalli|9.00|5.00|45.00|70000|South|FEANJ
41|1047|FE of Anjanapura 9th Block, Gollahalli|9.00|4.60|41.40|70000|South|FEANJ
42|1027|FE of Anjanapura 9th Block, Gollahalli|7.00|12.00|84.00|70000|South|FEANJ
43|1070|FE of Anjanapura 9th Block, Gollahalli|9.00|5.50|49.50|70000|South|FEANJ
44|260|FE of Banashankari 6th Stage, 4th 'B' Block, B.M. Kaval|18|12.00|216.00|70000|South|FEBSK
45|428|FE of Banashankari 6th Stage, 4th 'B' Block, B.M. Kaval|18.00|12.00|216.00|70000|South|FEBSK
46|876|FE of Banashankari 6th Stage, 4th 'B' Block, B.M. Kaval|12.00|18.00|216.00|70000|South|FEBSK
47|348/N|FE of Banashankari 6th Stage, 4th 'B' Block, B.M. Kaval|9.00|12.00|108.00|70000|South|FEBSK
48|522|FE of Banashankari 6th Stage, 4th 'B' Block, B.M. Kaval|(15.00+13.00)/2|24.00|336.00|70000|South|FEBSK
49|657|FE of Banashankari 6th Stage, 4th 'B' Block, B.M. Kaval|(21.00+22.00)/2|24.00|516.00|70000|South|FEBSK
50|998|FE of Banashankari 6th Stage, 4th 'B' Block, U.M. Kaval|18.00|(10.00+5.00)/2|135.00|70000|South|FEBSK
51|1063|FE of Banashankari 6th Stage, 4th 'B' Block, U.M. Kaval|18.00|(3.00+12.00)/2|135.00|70000|South|FEBSK
52|1060|FE of Banashankari 6th Stage, 4th 'B' Block, U.M. Kaval|18.00|(17.00+21.60)/2|347.40|70000|South|FEBSK
53|998|FE of Banashankari 6th Stage, 4th 'B' Block, U.M. Kaval|18.00|[10.00+5.00]/2|135.00|70000|South|FEBSK
54|1063|FE of Banashankari 6th Stage, 4th 'B' Block, U.M. Kaval|18.00|[3.00+12.00]/2|135.00|70000|South|FEBSK
55|378|FE of Banashankari 6th Stage, 4th 'H' Block|(11.00+15.00)/2|18.00|234.00|70000|South|FEBSK
56|372B|FE of Banashankari 6th Stage, 4th 'H' Block|18.00|(8.50+20.00)/2|256.50|70000|South|FEBSK
57|395/A|FE of Banashankari 6th Stage, 4th 'H' Block|12.00|(9.00+1.50)/2|63.00|70000|South|FEBSK
58|941|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|[10.50+11.00]/2|18.00|193.50|70000|South|FEBSK
59|957|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|6.00|12.00|72.00|70000|South|FEBSK
60|958|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|[6.50+6.00]/2|56.25|70000|South|FEBSK
61|963|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|6.00|54.00|70000|South|FEBSK
62|969|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|[5.50+6.50]/2|54.00|70000|South|FEBSK
63|970|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|[6.00+4.50]/2|47.25|70000|South|FEBSK
64|975|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|[7.80+10.00]/2|80.10|70000|South|FEBSK
65|976|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|[6.00+3.00]/2|40.50|70000|South|FEBSK
66|978|FE of Banashankari 6th Stage, 4th 'T' Block, U.M. Kaval|9.00|[6.00+5.00]/2|49.50|70000|South|FEBSK
67|48/A|JP Nagar 8th Phase, 2nd (EWS) Block, Thippasandra Village|20.00|5.00|100.00|100000|South|JPN8
68|79/A|JP Nagar 8th Phase, 2nd (EWS) Block, Thippasandra Village|9.00|12.00|108.00|100000|South|JPN8
69|74|JP Nagar 9th Phase, 2nd Block, Alahalli Village|[9.20+7.50]/2|12.19|101.78|100000|South|JPN9
70|73|JP Nagar 9th Phase, 2nd Block, Alahalli Village|11.7|12.19|142.62|100000|South|JPN9
71|432|JP Nagar 9th Phase, 2nd Block, Alahalli Village|18.28|[10.30+12.00]/2|203.82|100000|South|JPN9
72|745|JP Nagar 9th Phase, 3rd Block, Alahalli Village|[9.50+9.00]/2|6.00|55.50|100000|South|JPN9
73|726|JP Nagar 9th Phase, 3rd Block, Alahalli Village|9.00|6.00|54.00|100000|South|JPN9
74|725|JP Nagar 9th Phase, 3rd Block, Alahalli Village|9.00|6.00|54.00|100000|South|JPN9
75|705|JP Nagar 9th Phase, 3rd Block, Alahalli Village|9.00|3.70|33.30|100000|South|JPN9
76|337|JP Nagar 9th Phase, 3rd Block, Alahalli Village|9.30|[5.00+6.00]/2|51.15|100000|South|JPN9
77|360|JP Nagar 9th Phase, 4th Block, Thippasandra|(9.00+4.00)/2|12.19|79.23|100000|South|JPN9
78|54|Kumaraswamy 1st Stage, Govindayanahalli|[7.70+2.20]/2|9.00|44.55|127000|South|KSL
79|10|Kumaraswamy 1st Stage, Govindayanahalli|[7.20+11.30]/2|9.00|83.25|127000|South|KSL
80|3007|Sir M. Vishweshwaraiah Layout, 1st Block|9.00|5.10|45.90|84000|West|SMV
81|1493|Sir M. Vishweshwaraiah Layout, 1st Block, Nagadevanahalli|13.30|24.00|319.20|84000|West|SMV
82|1635|Sir M. Vishweshwaraiah Layout, 1st Block, Nagadevanahalli|11.60|18.00|208.80|84000|West|SMV
83|1512|Sir M. Vishweshwaraiah Layout, 1st Block, Nagadevanahalli|13.30|24.00|319.20|84000|West|SMV
84|2409/1|Sir M. Vishweshwaraiah Layout, 3rd Block, Ramasandra|12.00|6.70|80.40|84000|West|SMV
85|3359|Sir M. Vishweshwaraiah Layout, 4th Block, Ramasandra|10.5|18.00|189.00|84000|West|SMV
86|2936|Sir M. Vishweshwaraiah Layout, 4th Block, Ramasandra|12.00|11.70|140.40|84000|West|SMV
87|539|Sir M. Vishweshwaraiah Layout, 4th Block, Ramasandra|18.00|12.00|216.00|84000|West|SMV
88|1748|Sir M. Vishweshwaraiah Layout, 4th Block, Ramasandra|8.20|12.00|98.40|84000|West|SMV
89|1598|Sir M. Vishweshwaraiah Layout, 4th Block, Ramasandra|(7.00+5.8)/2|12.00|76.80|84000|West|SMV
90|755/A|Sir M. Vishweshwaraiah Layout, 6th Block, Ullalu|18.00|9.30|167.40|84000|West|SMV
91|187|Arkavathi 11th Block, Srirampura|9|7|63.00|87500|North|ARKJ
92|225|Arkavathi 15th Block, Thanisandra|18.2|(12.5+11.70)/2|220.22|87500|North|ARKT
93|244|Arkavathi 15th Block, Thanisandra|15|(10.00+11.2)/2|159.00|87500|North|ARKT
94|237|Arkavathi 15th Block, Thanisandra|15|(9.6+11.00)/2|154.50|87500|North|ARKT
95|684|Arkavathi 18th Block, Byrathikhane|18|(15.50+9.80)/2|227.70|87500|North|ARKB
96|566|Arkavathi 18th Block, Byrathikhane|(8.35+18.50)/2|18|241.60|87500|North|ARKB
97|HN348|Arkavathi 20th Block, Hennur|12|18|216.00|73500|North|ARKH
98|2204E|Arkavathi 2nd Block, Jakkur|24|(4.00+14.00)/2|216.00|73500|North|ARKJ
99|3188|Arkavathi 2nd Block, Sampigehalli|18|(6.00+13.00)/2|171.00|87500|North|ARKS
100|959|Arkavathi 3rd Block, Sampigehalli|(15.40+12.85)/2|18|254.25|87500|North|ARKS
101|556|Arkavathi 3rd Block, Venkateshapura|(10.90+11.50)/2|18|201.60|75000|North|ARKS
102|KNP396|Arkavathi 5th Block, K. Narayanapura|(6.00+22.40)/2|(9.00+18.70)/2|196.67|75000|North|ARKK
103|181|Arkavathi Layout 11th Block, Rachenahalli|5.50|9.00|49.50|71000|North|ARKT
104|304|Arkavathi Layout 11th Block, Rachenahalli|9.00|6.00|54.00|71000|North|ARKT
105|TS540|Arkavathi Layout, 15th & 20th Block, Thanisandra|(1) 3.6 (2) 14.4|(1) 12.00 (2) 0.5x12|129.60|87500|North|ARKT
106|TS484|Arkavathi Layout, 15th Block, Thanisandra|17.50|(9.00+7.00)/2|140.00|87500|North|ARKT
107|416A|Arkavathi Layout, 18th Block, Byrathikhane|12.00|(5.35+2.70)/2|48.30|87500|North|ARKB
108|522|Arkavathi Layout, 18th Block, Byrathikhane|24.00|(16.15+12.55)/2|344.40|87500|North|ARKB
109|552|Arkavathi Layout, 18th Block, Byrathikhane|(12.55+21.74)/2|14.30|245.17|87500|North|ARKB
110|498|Arkavathi Layout, 18th Block, Byrathikhane|24.00|(13.05+9.83)/2|274.56|87500|North|ARKB
111|513|Arkavathi Layout, 18th Block, Byrathikhane|24.00|(9.83+6.60)/2|197.16|87500|North|ARKB
112|516|Arkavathi Layout, 18th Block, Byrathikhane|24.00|(16.10+11.98)/2|336.96|87500|North|ARKB
113|506|Arkavathi Layout, 18th Block, Byrathikhane|24.00|(17.10+6.40)/2|282.00|87500|North|ARKB
114|548|Arkavathi Layout, 18th Block, Byrathikhane|(22.16+15.85)/2|14.65|278.42|87500|North|ARKB
115|453|Arkavathi Layout, 18th Block, Byrathikhane|12.00|(11.70+9.05)/2|124.50|87500|North|ARKB
116|532|Arkavathi Layout, 18th Block, Byrathikhane|24.00|(11.90+2.60)/2|174.00|87500|North|ARKB
117|221|Arkavathi Layout, 18th Block, Byrathikhane|(5.00+11.50)/2|9.00|74.25|87500|North|ARKB
118|222|Arkavathi Layout, 18th Block, Byrathikhane|(5.50+11.90)/2|9.00|78.30|87500|North|ARKB
119|270A|Arkavathi Layout, 18th Block, Byrathikhane|(7.50+10.70)/2|6.00|54.60|87500|North|ARKB
120|310|Arkavathi Layout, 18th Block, Byrathikhane|(6.00+9.50)/2|12.00|93.00|87500|North|ARKB
121|271|Arkavathi Layout, 18th Block, Byrathikhane|(14.00+10.70)/2|6.00|74.10|87500|North|ARKB
122|1308|Arkavathi Layout, 19th Block, Challakere|10.20|9.30|47.43|75000|North|ARKK
123|TS834A|Arkavathi Layout, 20th Block, Thanisandra|(9.2+9.00)/2|12.00|109.20|87500|North|ARKT
124|TS837B|Arkavathi Layout, 20th Block, Thanisandra|(9.2+3.50)/2|12.00|76.20|87500|North|ARKT
125|344D|Arkavathi Layout, 2nd Block, Sampigehalli|(16.34+16.62)/2|(25.13+22.95)/2|393.10|87500|North|ARKS
126|360|Arkavathi Layout, 2nd Block, Sampigehalli|18|20.5|369.00|87500|North|ARKS
127|385|Arkavathi Layout, 2nd Block, Sampigehalli|18|20|360.00|87500|North|ARKS
128|402|Arkavathi Layout, 2nd Block, Sampigehalli|18.00|20.00|360.00|87500|North|ARKS
129|2432|Arkavathi Layout, 2nd Block, Sampigehalli|9.00|6.00|54.00|87500|North|ARKS
130|1075|Arkavathi Layout, 3rd Block, Sampigehalli|12.00|(5.00+5.50)/2|63.00|87500|North|ARKS
131|1047|Arkavathi Layout, 3rd Block, Sampigehalli|5.00|12.00|60.00|87500|North|ARKS
132|1048|Arkavathi Layout, 3rd Block, Sampigehalli|5.00|12.00|60.00|87500|North|ARKS
133|2650A|Arkavathi Layout, 7th Block, Jakkur|(3.8+3.4)/2|9|32.40|73500|North|ARKJ
134|JK334|Arkavathi Layout, 7th Block, Jakkur|(1) (10+9.8)/2 (2) 9.8|(1) 8.00 (2) 0.5x15.00|152.20|73500|North|ARKJ
135|1995|Arkavathi Layout, 7th Block, Jakkur|(3.50+4.80)/2|9|37.35|73500|North|ARKJ
136|1002|Arkavathi Layout, 3rd Block, Venkateshapura|(3.00+3.40)/2|9|28.80|75000|North|ARKS
137|1019|Arkavathi Layout, 8th Block, Venkateshapura|(3.90+4.10)/2|9|36.00|75000|North|ARKS
138|3C-319|East of NGEF, Banasawadi|(3.02+9.10)/2|(12.0+14.60)/2|81.79|140000|North|NGEF
C1|3481|FE of Banashankari 6th Stage, 4th 'H' Block|(4.0+5.41)/2|(10.54+12.00)/2|52.00|70000|South|FEBSK
C2|853|Banashankari 6th Stage, 10th Block, Hemmigepura|24.00|(12.30+20.30)/2|391.20|65000|South|BSK6O
C3|317|Banashankari 6th Stage, 11th Block, Ganakallu|(7.30+1.50)/2|12.00|52.80|84000|South|BSK6O
C4|1332|FE of Anjanapura 11th Block, Kembathalli|8.60|12.00|103.20|77800|South|FEANJ
C5|1362|FE of Anjanapura 11th Block, Kembathalli|9.00|12.00|108.00|77800|South|FEANJ
C6|1333|FE of Anjanapura 11th Block, Kembathalli|8.60|12.00|103.20|77800|South|FEANJ
C7|271|FE of Anjanapura 11th Block, Kembathalli|12.00|6.20|74.40|77800|South|FEANJ
C8|1363|FE of Anjanapura 11th Block, Kembathalli|9.00|12.00|108.00|77800|South|FEANJ
"""
WITHDRAWN = {'7','8','26','27','53','54','55','56'}

# Approx coordinates for sites missing on the BDA geotag map (block cluster centroid or locality).
LOCALITY = {
 'Banashankari 6th Stage, 10th Block, Hemmigepura': (12.8835, 77.4880, 'locality: Hemmigepura (OSM)'),
 'Arkavathi 5th Block, K. Narayanapura': (13.0631, 77.6440, 'locality: K. Narayanapura (OSM)'),
 'Arkavathi Layout 11th Block, Rachenahalli': (13.0580, 77.6233, 'locality: Arkavathy 11th Block, Rachenahalli (OSM)'),
 'Sir M. Vishweshwaraiah Layout, 6th Block, Ullalu': (12.9535, 77.4800, 'locality: Ullal (OSM)'),
 'East of NGEF, Banasawadi': (13.0035, 77.6625, 'locality: East of NGEF / Kasturi Nagar (approx.)'),
}

