import React from 'react';

const SOLDIER_COLOR = { INFANTRY: '#38bdf8', SNIPER: '#22c55e', GUNNER: '#f59e0b' };

/** Live tactical layer: soldiers, helicopters, and animated armored convoy formation. */
export default function SimOverlay({ sim, view }) {
  const { u } = view;
  const slots = {};
  const soldiers = sim.soldiers.map((s) => {
    const key = s.status === 'MOVING' || s.status === 'FLYING' ? s.id : s.vertex;
    const n = (slots[key] = (slots[key] ?? -1) + 1);
    return { ...s, dx: (n - 1) * u * 2.2, dy: u * 4.2 };
  });

  const moving = (s) => s.status === 'MOVING' || s.status === 'FLYING';
  const enemies = sim.convoy.enemies;
  const aliveEnemies = enemies.filter((e) => e.alive);
  const totalHp = enemies.reduce((acc, e) => acc + (e.alive ? e.hp : 0), 0);
  const maxHp = enemies.reduce((acc, e) => acc + e.max_hp, 0);
  const [cx, cy] = sim.convoy.xy;

  return (
    <g className="sim-overlay">
      {/* Soldiers */}
      {soldiers.map((s) => (
        <g key={s.id} opacity={s.status === 'WAITING' ? 0.45 : 1}>
          <circle
            cx={s.xy[0] + (moving(s) ? 0 : s.dx)}
            cy={s.xy[1] + (moving(s) ? -u * 2.2 : s.dy)}
            r={u * 1.25}
            fill={SOLDIER_COLOR[s.type] || '#38bdf8'}
            stroke="#ffffff"
            strokeWidth={u * 0.35}
          />
        </g>
      ))}

      {/* Helicopter Flights */}
      {sim.flights.map((f) => (
        <g key={f.id} transform={`translate(${f.xy[0]}, ${f.xy[1]})`}>
          <circle r={u * 2.8} fill="#0f172a" stroke="#38bdf8" strokeWidth={u * 0.4} />
          <path d={`M ${-u * 2.2} 0 L ${u * 2.2} 0 M 0 ${-u * 2.2} L 0 ${u * 2.2}`} stroke="#38bdf8" strokeWidth={u * 0.5} className="spin" />
        </g>
      ))}

      {/* Convoy Formation */}
      {aliveEnemies.length > 0 && (
        <g transform={`translate(${cx}, ${cy})`}>
          {/* Tactical Danger Pulse */}
          <circle r={u * 4.2} fill="rgba(225, 29, 72, 0.2)" className="pulse" />
          
          {/* Armored Convoy Hull */}
          <rect x={-u * 2.6} y={-u * 1.8} width={u * 5.2} height={u * 3.6} rx={u * 0.8} fill="#e11d48" stroke="#ffffff" strokeWidth={u * 0.5} />
          
          {/* Cannon Barrel */}
          <rect x={u * 2.4} y={-u * 0.4} width={u * 1.4} height={u * 0.8} rx={u * 0.2} fill="#9f1239" />
          
          {/* Treads */}
          <rect x={-u * 2.4} y={-u * 2.2} width={u * 4.8} height={u * 0.6} fill="#881337" rx={u * 0.2} />
          <rect x={-u * 2.4} y={u * 1.6} width={u * 4.8} height={u * 0.6} fill="#881337" rx={u * 0.2} />
          
          {/* Alive Machines Count */}
          <text y={u * 0.8} textAnchor="middle" fontSize={u * 2.2} fontWeight="800" fill="#ffffff">
            {aliveEnemies.length}
          </text>

          {/* Floating Health Bar above Convoy */}
          <rect x={-u * 3.5} y={-u * 4.2} width={u * 7.0} height={u * 1.0} fill="#334155" rx={u * 0.3} />
          <rect
            x={-u * 3.5}
            y={-u * 4.2}
            width={Math.max(0, (totalHp / maxHp) * u * 7.0)}
            height={u * 1.0}
            fill={totalHp / maxHp > 0.4 ? '#22c55e' : '#f59e0b'}
            rx={u * 0.3}
          />
        </g>
      )}
    </g>
  );
}
