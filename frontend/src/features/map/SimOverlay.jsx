import React from 'react';
import { SOLDIER_COLOR, onTheMove } from './mapLabels';

/** Live tactical layer: travelling soldiers, helicopters and the armored convoy (idle squads are labels). */
export default function SimOverlay({ sim, view }) {
  const { u, font } = view;
  const enemies = sim.convoy.enemies;
  const aliveEnemies = enemies.filter((e) => e.alive);
  const totalHp = aliveEnemies.reduce((acc, e) => acc + e.hp, 0);
  const maxHp = enemies.reduce((acc, e) => acc + e.max_hp, 0);
  const [cx, cy] = sim.convoy.xy;

  return (
    <g className="sim-overlay">
      {sim.soldiers.filter(onTheMove).map((s) => (
        <circle key={s.id} cx={s.xy[0]} cy={s.xy[1] - u * 2.2} r={u * 1.25}
          fill={SOLDIER_COLOR[s.type] || '#38bdf8'} stroke="#ffffff" strokeWidth={u * 0.35} />
      ))}

      {sim.flights.map((f) => (
        <g key={f.id} transform={`translate(${f.xy[0]}, ${f.xy[1]})`}>
          <circle r={u * 2.8} fill="#0f172a" stroke="#38bdf8" strokeWidth={u * 0.4} />
          <path d={`M ${-u * 2.2} 0 L ${u * 2.2} 0 M 0 ${-u * 2.2} L 0 ${u * 2.2}`} stroke="#38bdf8" strokeWidth={u * 0.5} className="spin" />
        </g>
      ))}

      {aliveEnemies.length > 0 && (
        <g transform={`translate(${cx}, ${cy})`}>
          <circle r={u * 4.2} fill="rgba(225, 29, 72, 0.2)" className="pulse" />
          <rect x={-u * 2.6} y={-u * 1.8} width={u * 5.2} height={u * 3.6} rx={u * 0.8} fill="#e11d48" stroke="#ffffff" strokeWidth={u * 0.5} />
          <rect x={u * 2.4} y={-u * 0.4} width={u * 1.4} height={u * 0.8} rx={u * 0.2} fill="#9f1239" />
          <rect x={-u * 2.4} y={-u * 2.2} width={u * 4.8} height={u * 0.6} fill="#881337" rx={u * 0.2} />
          <rect x={-u * 2.4} y={u * 1.6} width={u * 4.8} height={u * 0.6} fill="#881337" rx={u * 0.2} />

          {/* Machines still alive and their joint health */}
          <text className="map-label" y={font * 0.36} textAnchor="middle" fontSize={font} fontWeight="800" style={{ fill: '#ffffff' }}>
            {aliveEnemies.length}
          </text>
          <rect x={-u * 3.5} y={-u * 4.2} width={u * 7} height={u} fill="#334155" rx={u * 0.3} />
          <rect x={-u * 3.5} y={-u * 4.2} width={Math.max(0, (totalHp / maxHp) * u * 7)} height={u}
            fill={totalHp / maxHp > 0.4 ? '#22c55e' : '#f59e0b'} rx={u * 0.3} />
        </g>
      )}
    </g>
  );
}
