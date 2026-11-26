import React from 'react';
import { byId, heatColor, midpoint } from './mapGeometry';

/** Corridors of labyrinth GM. Rendered as a canyon track bed with danger heat gradient. */
export function CorridorLayer({ graphM, view, simCorridors, covered = [], showCoverage, routeIds = [] }) {
  const verts = byId(graphM.vertices);
  const live = byId(simCorridors);
  const maxDanger = Math.max(1, ...(simCorridors ?? []).map((c) => c.danger));
  return (
    <g className="corridor-layer">
      {graphM.corridors.map((c) => {
        const a = verts[c.u].coords;
        const b = verts[c.v].coords;
        const danger = live[c.id]?.danger ?? 0;
        const isCovered = showCoverage && covered.includes(c.id);
        const m = midpoint(a, b);
        const stroke = simCorridors ? heatColor(danger / maxDanger) : isCovered ? '#16a34a' : '#d97706';
        // Compute normal vector to offset label perpendicularly away from overlapping edges
        const dx = b[0] - a[0];
        const dy = b[1] - a[1];
        const len = Math.hypot(dx, dy) || 1;
        const nx = -dy / len;
        const ny = dx / len;
        const labelX = m[0] + nx * view.u * 3.2;
        const labelY = m[1] + ny * view.u * 3.2;

        return (
          <g key={c.id}>
            {/* Wide canyon floor track */}
            <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke="#cbd5e1" strokeWidth={view.u * 3.6}
              strokeLinecap="round" opacity="0.65" />
            {routeIds.includes(c.id) && (
              <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke="#f59e0b" strokeWidth={view.u * 2.8}
                strokeLinecap="round" opacity="0.75" />
            )}
            {/* Center convoy guideline */}
            <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={stroke}
              strokeWidth={view.u * (isCovered ? 1.6 : 1.1)} strokeDasharray={`${view.u * 2} ${view.u * 1.5}`}
              strokeLinecap="round" opacity={0.95} />
            {isCovered && <circle cx={m[0]} cy={m[1]} r={view.u * 1.1} fill="#16a34a" stroke="#ffffff" strokeWidth={view.u * 0.4} />}
            <g transform={`translate(${labelX}, ${labelY})`}>
              <rect x={-view.u * 3.2} y={-view.u * 1.2} width={view.u * 6.4} height={view.u * 2.4} rx={view.u * 0.5}
                fill="rgba(241, 245, 249, 0.85)" stroke="#cbd5e1" strokeWidth={view.u * 0.2} />
              <text x={0} y={view.u * 0.5} fontSize={view.u * 1.9} textAnchor="middle" fill="#475569" fontWeight="600">
                {c.id}
              </text>
            </g>
          </g>
        );
      })}
    </g>
  );
}

/** Elevated walkways and bridges of GE with parallel rails, elevation shadow and health badges. */
export function EdgeLayer({ graphE, view, treeIds = [], showTree, bridges }) {
  const verts = byId(graphE.vertices);
  const live = byId(bridges);
  return (
    <g className="edge-layer">
      {graphE.edges.map((e) => {
        const a = verts[e.u].coords;
        const b = verts[e.v].coords;
        const br = live[e.id];
        const isBridge = !!br || e.is_bridge;
        const inTree = showTree && treeIds.includes(e.id);
        const hurt = br && br.hp < br.max_hp;
        const stroke = br?.destroyed ? '#ef4444' : inTree ? '#2563eb' : hurt ? '#eab308' : isBridge ? '#0284c7' : '#64748b';
        const m = midpoint(a, b);
        const dx = b[0] - a[0];
        const dy = b[1] - a[1];
        const len = Math.hypot(dx, dy) || 1;
        const nx = -dy / len;
        const ny = dx / len;

        return (
          <g key={e.id}>
            {/* Walkway shadow */}
            <line x1={a[0]} y1={a[1] + view.u * 0.8} x2={b[0]} y2={b[1] + view.u * 0.8}
              stroke="rgba(15, 23, 42, 0.12)" strokeWidth={view.u * (inTree ? 2.8 : 2.0)} strokeLinecap="round" />
            {/* Distinctive bridge double parallel rails */}
            {isBridge && !br?.destroyed && (
              <>
                <line x1={a[0] + nx * view.u * 1.2} y1={a[1] + ny * view.u * 1.2}
                  x2={b[0] + nx * view.u * 1.2} y2={b[1] + ny * view.u * 1.2}
                  stroke={stroke} strokeWidth={view.u * 0.6} strokeDasharray={`${view.u * 1.5} ${view.u}`} />
                <line x1={a[0] - nx * view.u * 1.2} y1={a[1] - ny * view.u * 1.2}
                  x2={b[0] - nx * view.u * 1.2} y2={b[1] - ny * view.u * 1.2}
                  stroke={stroke} strokeWidth={view.u * 0.6} strokeDasharray={`${view.u * 1.5} ${view.u}`} />
              </>
            )}
            {/* Main walkway beam */}
            <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={stroke}
              strokeWidth={view.u * (inTree ? 2.2 : isBridge ? 1.6 : 1.2)} strokeLinecap="round"
              strokeDasharray={br?.destroyed ? `${view.u * 1.2} ${view.u * 1.2}` : undefined}
              opacity={showTree && !inTree ? 0.35 : 1} />
            {/* Bridge health badge */}
            {br && (
              <g transform={`translate(${m[0]}, ${m[1] - view.u * 2.0})`}>
                <rect x={-view.u * 3.6} y={-view.u * 1.5} width={view.u * 7.2} height={view.u * 2.5} rx={view.u * 0.6}
                  fill={br.destroyed ? '#fef2f2' : hurt ? '#fefce8' : '#f0f9ff'}
                  stroke={br.destroyed ? '#ef4444' : hurt ? '#ca8a04' : '#0284c7'} strokeWidth={view.u * 0.3} />
                <text x={0} y={view.u * 0.2} className="map-label" fontSize={view.u * 1.8} textAnchor="middle"
                  fill={br.destroyed ? '#dc2626' : hurt ? '#854d0e' : '#0369a1'} fontWeight="700">
                  {br.destroyed ? (br.waiting_crew ? '✕ sin cuadrilla' : `✕ ${br.repair_left}s`) : `${br.hp}/${br.max_hp}`}
                </text>
              </g>
            )}
          </g>
        );
      })}
    </g>
  );
}

/** Tower surveillance bubble with tactical concentric radar sweeps. */
export function RadiusLayer({ towers, view }) {
  return (
    <g className="radius-layer">
      {towers.map((t) => {
        const cx = t.xy?.[0] ?? t.x;
        const cy = t.xy?.[1] ?? t.y;
        return (
          <g key={t.vertex_id}>
            <circle cx={cx} cy={cy} r={t.rv}
              fill="rgba(59, 130, 246, 0.08)" stroke="#3b82f6" strokeWidth={view.u * 0.5}
              strokeDasharray={`${view.u * 2.5} ${view.u * 2.5}`} />
            <circle cx={cx} cy={cy} r={t.rv * 0.5}
              fill="none" stroke="#60a5fa" strokeWidth={view.u * 0.25} strokeDasharray={`${view.u * 1.5} ${view.u * 3}`} />
          </g>
        );
      })}
    </g>
  );
}
