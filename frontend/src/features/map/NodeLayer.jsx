import React from 'react';

const TYPE_LABEL = { BASE: 'Base Principal', CANDIDATE: 'Torre Candidata', TRANSIT: 'Punto de Tránsito', HELIPORT: 'Helipuerto' };
export const typeLabel = (t) => TYPE_LABEL[t] ?? t;

/** One vertex marker of GE (its name and soldier places are drawn by the label layer). */
function NodeE({ v, view, isTower, onSelect, selected }) {
  const [x, y] = v.coords;
  const r = view.u * 1.9;
  const stroke = isTower ? '#b45309' : selected ? '#2563eb' : '#334155';
  const fill = v.type === 'BASE' ? '#2563eb' : isTower ? '#f59e0b' : v.type === 'CANDIDATE' ? '#e2e8f0' : '#cbd5e1';
  return (
    <g className="map-node node-ge" onClick={() => onSelect({ ...v, network: 'GE' })} tabIndex={0}
      filter="url(#node-shadow)" onKeyDown={(e) => e.key === 'Enter' && onSelect({ ...v, network: 'GE' })}>
      {selected && <circle cx={x} cy={y} r={r * 2.2} fill="none" stroke="#2563eb" strokeWidth={view.u * 0.6} strokeDasharray={`${view.u * 1.5} ${view.u}`} />}
      {v.type === 'BASE' && (
        <g>
          <rect x={x - r * 1.2} y={y - r * 1.2} width={r * 2.4} height={r * 2.4} rx={r * 0.4} fill="#2563eb" stroke="#1d4ed8" strokeWidth={view.u * 0.5} />
          <polygon points={`${x},${y - r * 0.7} ${x + r * 0.7},${y} ${x},${y + r * 0.7} ${x - r * 0.7},${y}`} fill="#ffffff" />
        </g>
      )}
      {v.type === 'CANDIDATE' && (
        <g>
          <polygon points={`${x},${y - r * 1.4} ${x + r * 1.3},${y} ${x},${y + r * 1.4} ${x - r * 1.3},${y}`}
            fill={fill} stroke={stroke} strokeWidth={view.u * (isTower ? 0.8 : 0.4)} />
          {isTower && <circle cx={x} cy={y} r={r * 0.45} fill="#b45309" />}
        </g>
      )}
      {v.type === 'TRANSIT' && <circle cx={x} cy={y} r={r * 0.75} fill={fill} stroke={stroke} strokeWidth={view.u * 0.4} />}
      {v.type === 'HELIPORT' && (
        <g>
          <circle cx={x} cy={y} r={r * 1.3} fill="#0284c7" stroke="#0369a1" strokeWidth={view.u * 0.6} />
          <text x={x} y={y + view.u * 0.9} textAnchor="middle" fontSize={view.u * 2.2} fontWeight="800" fill="#ffffff">H</text>
        </g>
      )}
    </g>
  );
}

/** One vertex marker of GM (corridor junctions). */
function NodeM({ v, view, onSelect, selected }) {
  const [x, y] = v.coords;
  const s = view.u * 1.4;
  const fill = v.is_entry ? '#16a34a' : v.is_exit ? '#dc2626' : '#ea580c';
  const border = v.is_entry ? '#15803d' : v.is_exit ? '#b91c1c' : '#c2410c';
  return (
    <g className="map-node node-gm" onClick={() => onSelect({ ...v, network: 'GM' })} tabIndex={0}
      filter="url(#node-shadow)" onKeyDown={(e) => e.key === 'Enter' && onSelect({ ...v, network: 'GM' })}>
      {selected && <circle cx={x} cy={y} r={s * 2.4} fill="none" stroke="#dc2626" strokeWidth={view.u * 0.6} />}
      <rect x={x - s} y={y - s} width={s * 2} height={s * 2} rx={s * 0.25} fill={fill} stroke={border}
        strokeWidth={view.u * 0.5} transform={`rotate(45 ${x} ${y})`} />
    </g>
  );
}

export function NodeLayer({ graphE, graphM, view, showE, showM, towerIds, onSelect, selected }) {
  return (
    <g className="nodes-group">
      {showM && graphM.vertices.map((v) => (
        <NodeM key={v.id} v={v} view={view} onSelect={onSelect} selected={selected?.id === v.id} />
      ))}
      {showE && graphE.vertices.map((v) => (
        <NodeE key={v.id} v={v} view={view} isTower={towerIds.includes(v.id)} onSelect={onSelect}
          selected={selected?.id === v.id} />
      ))}
    </g>
  );
}
