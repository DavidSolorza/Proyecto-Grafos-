import React, { useEffect, useRef } from 'react';
import { sound } from '../../services/soundEffects';

const LASER_COLOR = { INFANTRY: '#38bdf8', SNIPER: '#22c55e', GUNNER: '#f59e0b' };

export default function CombatEffectsLayer({ sim, view }) {
  const prevEventsLen = useRef(0);
  const { u } = view;

  useEffect(() => {
    if (!sim) return;
    const len = sim.events.length;
    if (len > prevEventsLen.current) {
      const recent = sim.events.slice(prevEventsLen.current);
      recent.forEach((e) => {
        if (e.kind === 'combat') sound.playShoot();
        if (e.kind === 'buy') sound.playRecruit();
        if (e.kind === 'convoy' && e.text.includes('destruid')) {
          sound.playExplosion();
          sound.playCoin();
        }
        if (e.kind === 'end') {
          if (e.text.includes('Victoria')) sound.playVictory();
          else sound.playDefeat();
        }
      });
      prevEventsLen.current = len;
    }
  }, [sim]);

  if (!sim || !sim.convoy || sim.convoy.enemies.every((e) => !e.alive)) return null;

  const [cx, cy] = sim.convoy.xy;
  const recentCombat = sim.events.filter((e) => e.kind === 'combat' && sim.clock - e.t < 0.6);
  const activeSoldiers = sim.soldiers.filter((s) => s.status === 'STATIONED');

  return (
    <g className="combat-effects-layer" pointerEvents="none">
      {recentCombat.map((e, idx) => {
        const shooter = activeSoldiers.find((s) => e.text.includes(s.id));
        if (!shooter) return null;
        const color = LASER_COLOR[shooter.type] || '#f59e0b';
        return (
          <g key={`${e.t}-${idx}`}>
            <line
              x1={shooter.xy[0]}
              y1={shooter.xy[1]}
              x2={cx}
              y2={cy}
              stroke={color}
              strokeWidth={u * 0.7}
              strokeDasharray={`${u * 2} ${u}`}
              opacity="0.85"
            />
            <circle cx={cx} cy={cy} r={u * 1.8} fill="none" stroke={color} strokeWidth={u * 0.5} className="pulse" />
          </g>
        );
      })}
    </g>
  );
}
