import React from 'react';

const TYPE_LABEL = { BASE: 'Base Principal', CANDIDATE: 'Torre Candidata', TRANSIT: 'Punto de Tránsito', HELIPORT: 'Helipuerto' };
export const typeLabel = (t) => TYPE_LABEL[t] ?? t;

/** One vertex of GE with 3 soldier capacity slots and high-contrast pill label. */
function NodeE({ v, view, isTower, onSelect, selected, occupancy }) {
  const [x, y] = v.coords;
  const r = view.u * 1.9;
  const stroke = isTower ? '#b45309' : selected ? '#2563eb' : '#334155';
  const fill = v.type === 'BASE' ? '#2563eb' : isTower ? '#f59e0b' : v.type === 'CANDIDATE' ? '#e2e8f0' : '#cbd5e1';
  const occ = occupancy?.occupants ?? 0;
  const res = occupancy?.reserved ?? 0;

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
      {/* High-contrast dark badge for node ID */}
      <g transform={`translate(${x}, ${y + r * 2.2})`}>
        <rect x={-view.u * 3.8} y={-view.u * 1.2} width={view.u * 7.6} height={view.u * 2.4} rx={view.u * 0.6}
          fill="rgba(15, 23, 42, 0.85)" />
        <text x={0} y={view.u * 0.5} textAnchor="middle" fontSize={view.u * 1.8} fontWeight="700" fill="#ffffff">
          {v.id}
        </text>
      </g>
      {/* 3 Capacity slot indicators on towers */}
      {isTower && (
        <g transform={`translate(${x}, ${y - r * 2.0})`}>
          {[0, 1, 2].map((slotIdx) => {
            const slotFill = slotIdx < occ ? '#16a34a' : slotIdx < (occ + res) ? '#f59e0b' : '#e2e8f0';
            return (
              <circle key={slotIdx} cx={(slotIdx - 1) * view.u * 1.8} cy={0} r={view.u * 0.6}
                fill={slotFill} stroke="#475569" strokeWidth={view.u * 0.25} />
            );
          })}
        </g>
      )}
    </g>
  );
}

/** One vertex of GM (corridor junctions) with dark pill badge and clear contrast. */
function NodeM({ v, view, onSelect, selected }) {
  const [x, y] = v.coords;
  const s = view.u * 1.4;
  const fill = v.is_entry ? '#16a34a' : v.is_exit ? '#dc2626' : '#ea580c';
  const border = v.is_entry ? '#15803d' : v.is_exit ? '#b91c1c' : '#c2410c';
  const labelText = v.is_entry ? `▶ ${v.id}` : v.is_exit ? `⚑ ${v.id}` : v.id;

  return (
    <g className="map-node node-gm" onClick={() => onSelect({ ...v, network: 'GM' })} tabIndex={0}
      filter="url(#node-shadow)" onKeyDown={(e) => e.key === 'Enter' && onSelect({ ...v, network: 'GM' })}>
      {selected && <circle cx={x} cy={y} r={s * 2.4} fill="none" stroke="#dc2626" strokeWidth={view.u * 0.6} />}
      <rect x={x - s} y={y - s} width={s * 2} height={s * 2} rx={s * 0.25} fill={fill} stroke={border}
        strokeWidth={view.u * 0.5} transform={`rotate(45 ${x} ${y})`} />
      {/* High contrast dark pill behind text */}
      <g transform={`translate(${x}, ${y - s * 2.2})`}>
        <rect x={-view.u * (v.is_entry || v.is_exit ? 5.2 : 3.8)} y={-view.u * 1.2}
          width={view.u * (v.is_entry || v.is_exit ? 10.4 : 7.6)} height={view.u * 2.4} rx={view.u * 0.6}
          fill="rgba(15, 23, 42, 0.90)" stroke={fill} strokeWidth={view.u * 0.25} />
        <text x={0} y={view.u * 0.5} textAnchor="middle" fontSize={view.u * 1.8} fontWeight="700" fill="#ffffff">
          {labelText}
        </text>
      </g>
    </g>
  );
}

export function NodeLayer({ graphE, graphM, view, showE, showM, towerIds, towers, onSelect, selected }) {
  return (
    <g className="nodes-group">
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
