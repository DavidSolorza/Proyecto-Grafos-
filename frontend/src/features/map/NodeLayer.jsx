import React from 'react';

const TYPE_LABEL = { BASE: 'Base', CANDIDATE: 'Candidata', TRANSIT: 'Tránsito', HELIPORT: 'Helipuerto' };
export const typeLabel = (t) => TYPE_LABEL[t] ?? t;

/** One vertex of GE. The shape tells the type: square = base, diamond = candidate, H = heliport. */
function NodeE({ v, view, isTower, onSelect, selected, occupancy }) {
  const [x, y] = v.coords;
  const r = view.u * 1.7;
  const stroke = isTower ? '#d9a441' : '#14110e';
  const fill = v.type === 'BASE' ? '#f0e7d6' : v.type === 'CANDIDATE' ? (isTower ? '#d9a441' : '#8a7a5c') : '#a89c84';
  return (
    <g className="map-node" onClick={() => onSelect({ ...v, network: 'GE' })} tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect({ ...v, network: 'GE' })}>
      {selected && <circle cx={x} cy={y} r={r * 1.9} fill="none" stroke="#f0e7d6" strokeWidth={view.u * 0.4} />}
      {v.type === 'BASE' && <rect x={x - r} y={y - r} width={r * 2} height={r * 2} rx={r * 0.3} fill={fill} stroke={stroke} strokeWidth={view.u * 0.5} />}
      {v.type === 'CANDIDATE' && <polygon points={`${x},${y - r * 1.2} ${x + r * 1.2},${y} ${x},${y + r * 1.2} ${x - r * 1.2},${y}`} fill={fill} stroke={stroke} strokeWidth={view.u * 0.5} />}
      {v.type === 'TRANSIT' && <circle cx={x} cy={y} r={r * 0.7} fill={fill} stroke={stroke} strokeWidth={view.u * 0.4} />}
      {v.type === 'HELIPORT' && (
        <>
          <circle cx={x} cy={y} r={r * 1.1} fill={fill} stroke={stroke} strokeWidth={view.u * 0.5} />
          <text x={x} y={y + view.u * 0.9} textAnchor="middle" fontSize={view.u * 2.4} fontWeight="700" fill="#14110e">H</text>
        </>
      )}
      <text x={x} y={y + r * 2.7} textAnchor="middle" className="map-label" fontSize={view.u * 2.2}>{v.id}</text>
      {isTower && occupancy && (
        <text x={x} y={y - r * 1.8} textAnchor="middle" className="map-label gold" fontSize={view.u * 2.3}>
          {occupancy.occupants + occupancy.reserved}/{occupancy.capacity}
        </text>
      )}
    </g>
  );
}

/** One vertex of GM (the labyrinth). Green = entry, red = exit. */
function NodeM({ v, view, onSelect, selected }) {
  const [x, y] = v.coords;
  const s = view.u * 1.3;
  const fill = v.is_entry ? '#8fb27c' : v.is_exit ? '#e0533a' : '#c7704f';
  return (
    <g className="map-node" onClick={() => onSelect({ ...v, network: 'GM' })} tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect({ ...v, network: 'GM' })}>
      {selected && <circle cx={x} cy={y} r={s * 2.2} fill="none" stroke="#f0e7d6" strokeWidth={view.u * 0.4} />}
      <rect x={x - s} y={y - s} width={s * 2} height={s * 2} fill={fill} stroke="#14110e" strokeWidth={view.u * 0.4} transform={`rotate(45 ${x} ${y})`} />
      <text x={x} y={y - s * 1.9} textAnchor="middle" className="map-label rust" fontSize={view.u * 2}>
        {v.is_entry ? `▶ ${v.id}` : v.is_exit ? `⚑ ${v.id}` : v.id}
      </text>
    </g>
  );
}

export function NodeLayer({ graphE, graphM, view, showE, showM, towerIds, towers, onSelect, selected }) {
  return (
    <g>
      {showM && graphM.vertices.map((v) => (
        <NodeM key={v.id} v={v} view={view} onSelect={onSelect} selected={selected?.id === v.id} />
      ))}
      {showE && graphE.vertices.map((v) => (
        <NodeE key={v.id} v={v} view={view} isTower={towerIds.includes(v.id)} onSelect={onSelect}
          selected={selected?.id === v.id} occupancy={towers?.find((t) => t.vertex_id === v.id)} />
      ))}
    </g>
  );
}
