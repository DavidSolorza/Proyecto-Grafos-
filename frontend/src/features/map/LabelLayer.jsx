import React from 'react';
import { placeLabels } from './labelLayout';
import { buildLabels } from './mapLabels';

const TONES = {
  plain: ['rgba(248, 250, 252, 0.94)', '#cbd5e1', '#475569'],
  bridge: ['#f0f9ff', '#0284c7', '#0369a1'],
  hurt: ['#fefce8', '#ca8a04', '#854d0e'],
  down: ['#fef2f2', '#ef4444', '#dc2626'],
};

/** Pill with its text, tower places or soldiers, centred on (0, 0). */
function Label({ item, view }) {
  const { u, font } = view;
  const { w, h, kind } = item;
  const [fill, stroke, ink] = kind === 'name' ? ['rgba(15, 23, 42, 0.9)', item.color ?? 'none', '#ffffff']
    : kind === 'tag' ? TONES[item.tone ?? 'plain'] : ['rgba(255, 255, 255, 0.95)', '#64748b', '#0f172a'];
  const text = (value, x, anchor = 'middle') => (
    <text className="map-label" x={x} y={font * 0.36} textAnchor={anchor} fontSize={font} fontWeight="700" style={{ fill: ink }}>
      {value}
    </text>
  );
  let cursor = -w / 2 + 3;
  return (
    <g transform={`translate(${item.x}, ${item.y})`}>
      <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={Math.min(h / 2, 6)} fill={fill} stroke={stroke} strokeWidth={1.2} />
      {(kind === 'name' || kind === 'tag') && text(item.text, 0)}
      {kind === 'slots' && [0, 1, 2].map((i) => (
        <circle key={i} cx={(i - 1) * u * 1.8} r={u * 0.65} stroke="#475569" strokeWidth={1}
          fill={i < item.used ? '#16a34a' : i < item.used + item.reserved ? '#f59e0b' : '#e2e8f0'} />
      ))}
      {kind === 'squad' && item.parts.map((p, i) => {
        const x = cursor + u * 1.2;
        cursor += item.compact ? u * 2.4 : u * 2.4 + p.text.length * font * 0.61 + 3;
        return (
          <g key={i} opacity={p.faded ? 0.45 : 1}>
            <circle cx={x} r={u} fill={p.color} stroke="#0f172a" strokeWidth={0.8} />
            {p.text && text(p.text, x + u * 1.2, 'start')}
          </g>
        );
      })}
    </g>
  );
}

/** Every text of the map is drawn here, on top, after solving where each one fits. */
export default function LabelLayer({ world, view, layers, towerIds }) {
  const { requests, blocked } = buildLabels({ world, view, layers, towerIds });
  return (
    <g className="label-layer" pointerEvents="none">
      {placeLabels(requests, blocked, view).map((item) => <Label key={item.id} item={item} view={view} />)}
    </g>
  );
}
