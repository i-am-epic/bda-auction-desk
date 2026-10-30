"""Assemble the single-file site: template + leaflet css + analysed data + packed tiles -> build/index.html"""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
b = lambda *p: os.path.join(here, 'build', *p)
t = open(os.path.join(here, 'template.html'), encoding='utf8').read()
data = json.load(open(b('data2.json'), encoding='utf8'))
t = t.replace('/*LEAFLETCSS*/', open(b('leaflet.css'), encoding='utf8').read())
t = t.replace('/*DATA*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
t = t.replace('/*TILES*/', open(b('tiles.json')).read())
open(b('index.html'), 'w', encoding='utf8').write(t)
print('index.html', os.path.getsize(b('index.html')))
