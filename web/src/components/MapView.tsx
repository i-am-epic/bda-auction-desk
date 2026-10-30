import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Polygon, CircleMarker, Tooltip, LayersControl, useMap } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import type { LatLngBoundsExpression } from 'leaflet';
import type { Site } from '../lib/types';
import { inr, VERDICT_TONE } from '../lib/format';

const css = (v: string) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const color = (s: Site) => css(`--${VERDICT_TONE[s.verdict]}`) || '#888';

function Fit({ bounds, focus }: { bounds: LatLngBoundsExpression | null; focus?: Site | null }) {
  const map = useMap();
  useEffect(() => { if (bounds && !focus) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 16 }); }, [bounds, focus, map]);
  useEffect(() => { if (focus) map.flyTo([focus.lat, focus.lon], 18, { duration: 0.8 }); }, [focus, map]);
  useEffect(() => { const t = setTimeout(() => map.invalidateSize(), 120); return () => clearTimeout(t); });
  return null;
}

function Basemaps({ satellite = true }: { satellite?: boolean }) {
  return (
    <LayersControl position="topright">
      <LayersControl.BaseLayer checked={satellite} name="Satellite">
        <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" maxZoom={19} maxNativeZoom={18}
          attribution="Imagery © Esri, Maxar, Earthstar Geographics" />
      </LayersControl.BaseLayer>
      <LayersControl.BaseLayer checked={!satellite} name="Streets">
        <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" maxZoom={19} attribution="© OpenStreetMap contributors" />
      </LayersControl.BaseLayer>
    </LayersControl>
  );
}

export function ExploreMap({ sites, hover, focus }: { sites: Site[]; hover: string | null; focus?: Site | null }) {
  const nav = useNavigate();
  const bounds = useMemo<LatLngBoundsExpression | null>(() => sites.length ? sites.map(s => [s.lat, s.lon] as [number, number]) : null, [sites]);
  return (
    <MapContainer center={[12.95, 77.57]} zoom={11} scrollWheelZoom style={{ height: '100%' }}>
      <Basemaps />
      <Fit bounds={bounds} focus={focus} />
      {sites.map(s => {
        const c = color(s), hot = hover === s.id;
        return (
          <span key={s.id}>
            <Polygon positions={s.polygon} pathOptions={{ color: s.polyDrawn ? '#ffffff' : c, weight: hot ? 4 : 2, dashArray: s.polyDrawn ? '4 3' : undefined, fillColor: c, fillOpacity: hot ? 0.75 : 0.5 }}
              eventHandlers={{ click: () => nav(`/site/${s.id}`) }} />
            <CircleMarker center={[s.lat, s.lon]} radius={hot ? 9 : 6} pathOptions={{ color: '#ffffff', weight: 1.5, fillColor: c, fillOpacity: 1 }}
              eventHandlers={{ click: () => nav(`/site/${s.id}`) }}>
              <Tooltip className="tip" direction="top" offset={[0, -6]}>
                <b>Site {s.site}</b> · {s.score ?? '–'}/10<br />{s.locality}<br />{s.areaSqft.toLocaleString('en-IN')} ft² · likely {inr(s.expTotal)}
              </Tooltip>
            </CircleMarker>
          </span>
        );
      })}
    </MapContainer>
  );
}

export function MiniMap({ s }: { s: Site }) {
  return (
    <div className="minimap">
      <MapContainer center={[s.lat, s.lon]} zoom={18} scrollWheelZoom={false} style={{ height: '100%' }}>
        <Basemaps />
        <Polygon positions={s.polygon} pathOptions={{ color: s.polyDrawn ? '#ffffff' : color(s), weight: 3, dashArray: s.polyDrawn ? '5 4' : undefined, fillColor: color(s), fillOpacity: 0.35 }} />
      </MapContainer>
    </div>
  );
}
