import React from 'react';

const SOLDIER_COLOR = { INFANTRY: '#8fb27c', SNIPER: '#f0e7d6', GUNNER: '#d9a441' };

/** Live layer: soldiers, helicopters and the convoy formation. */
export default function SimOverlay({ sim, view }) {
  const { u } = view;
  // Soldiers that share a vertex are spread in a small arc so they do not overlap
  const slots = {};
  const soldiers = sim.soldiers.map((s) => {
    const key = s.status === 'MOVING' || s.status === 'FLYING' ? s.id : s.vertex;
    const n = (slots[key] = (slots[key] ?? -1) + 1);
    return { ...s, dx: (n - 1) * u * 2.2, dy: u * 4.2 };
  });
  const moving = (s) => s.status === 'MOVING' || s.status === 'FLYING';
  const alive = sim.convoy.enemies.filter((e) => e.alive).length;
  const [cx, cy] = sim.convoy.xy;

  return (
    <g>
      {soldiers.map((s) => (
        <g key={s.id}>
          <circle cx={s.xy[0] + (moving(s) ? 0 : s.dx)} cy={s.xy[1] + (moving(s) ? -u * 2 : s.dy)} r={u * 1.1}
            fill={SOLDIER_COLOR[s.type]} stroke="#14110e" strokeWidth={u * 0.3}
            opacity={s.status === 'WAITING' ? 0.5 : 1} />
        </g>
      ))}
      {sim.flights.map((f) => (
        <g key={f.id}>
          <circle cx={f.xy[0]} cy={f.xy[1]} r={u * 2.6} fill="#14110e" stroke="#f0e7d6" strokeWidth={u * 0.4} />
          <text x={f.xy[0]} y={f.xy[1] + u * 0.9} textAnchor="middle" fontSize={u * 2.6} fill="#f0e7d6" fontWeight="700">✚</text>
        </g>
      ))}
      {alive > 0 && (
        <g>
          <circle cx={cx} cy={cy} r={u * 3.6} fill="rgba(224,83,50,0.25)" className="pulse" />
          <circle cx={cx} cy={cy} r={u * 2.2} fill="#e0533a" stroke="#f0e7d6" strokeWidth={u * 0.5} />
          <text x={cx} y={cy + u * 0.9} textAnchor="middle" fontSize={u * 2.4} fontWeight="700" fill="#14110e">{alive}</text>
        </g>
      )}
    </g>
  );
}
