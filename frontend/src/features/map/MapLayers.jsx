import React from 'react';
import { byId, heatColor, midpoint } from './mapGeometry';

/** Corridors of the labyrinth GM. In simulation they are coloured by danger. */
export function CorridorLayer({ graphM, view, simCorridors, covered = [], showCoverage }) {
  const verts = byId(graphM.vertices);
  const live = byId(simCorridors);
  const maxDanger = Math.max(1, ...(simCorridors ?? []).map((c) => c.danger));
  return (
    <g>
      {graphM.corridors.map((c) => {
        const a = verts[c.u].coords;
        const b = verts[c.v].coords;
        const danger = live[c.id]?.danger ?? 0;
        const isCovered = showCoverage && covered.includes(c.id);
        const m = midpoint(a, b);
        return (
          <g key={c.id}>
            <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
              stroke={simCorridors ? heatColor(danger / maxDanger) : '#c7704f'}
              strokeWidth={view.u * (isCovered ? 1.3 : 0.8)} strokeDasharray={`${view.u * 2} ${view.u * 1.4}`}
              strokeLinecap="round" opacity={isCovered || simCorridors ? 1 : 0.8} />
            {isCovered && <circle cx={m[0]} cy={m[1]} r={view.u * 0.9} fill="#8fb27c" />}
            <text x={m[0]} y={m[1] - view.u * 1.6} className="map-label dim" fontSize={view.u * 2.1} textAnchor="middle">
              {c.id}
            </text>
          </g>
        );
      })}
    </g>
  );
}

/** Edges (roads and bridges) of the elevated graph GE. */
export function EdgeLayer({ graphE, view, treeIds = [], showTree, bridges }) {
  const verts = byId(graphE.vertices);
  const live = byId(bridges);
  return (
    <g>
      {graphE.edges.map((e) => {
        const a = verts[e.u].coords;
        const b = verts[e.v].coords;
        const br = live[e.id];
        const inTree = showTree && treeIds.includes(e.id);
        const hurt = br && br.hp < br.max_hp;
        const stroke = br?.destroyed ? '#e0533a' : inTree ? '#8fb27c' : hurt ? '#d9a441' : '#e8dcc4';
        const m = midpoint(a, b);
        return (
          <g key={e.id}>
            <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={stroke}
              strokeWidth={view.u * (inTree ? 1.5 : 1)} strokeLinecap="round"
              strokeDasharray={br?.destroyed ? `${view.u} ${view.u}` : undefined}
              opacity={showTree && !inTree ? 0.35 : 0.95} />
            {br && (
              <text x={m[0]} y={m[1] - view.u * 1.4} className="map-label" fontSize={view.u * 2.1} textAnchor="middle"
                fill={br.destroyed ? '#e0533a' : '#e8dcc4'}>
                {br.destroyed ? (br.waiting_crew ? '✕ sin cuadrilla' : `✕ ${br.repair_left}s`) : `${br.hp}/${br.max_hp}`}
              </text>
            )}
          </g>
        );
      })}
    </g>
  );
}

/** Radius of surveillance Rv drawn around each chosen tower. */
export function RadiusLayer({ towers, view }) {
  return (
    <g>
      {towers.map((t) => (
        <circle key={t.vertex_id} cx={t.xy?.[0] ?? t.x} cy={t.xy?.[1] ?? t.y} r={t.rv}
          fill="rgba(184,137,59,0.10)" stroke="#d9a441" strokeWidth={view.u * 0.5} strokeDasharray={`${view.u * 2} ${view.u * 2}`} />
      ))}
    </g>
  );
}
