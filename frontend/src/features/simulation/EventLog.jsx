import React, { useEffect, useRef } from 'react';
import { ScrollText, Swords, Navigation, Wrench, ArrowRight, Plane, DollarSign, Flag } from 'lucide-react';

const ICONS = {
  combat: Swords,
  convoy: Navigation,
  bridge: Wrench,
  move: ArrowRight,
  air: Plane,
  buy: DollarSign,
  end: Flag,
};

/** Explains what happened and why in chronological order. Crisp light theme. */
export default function EventLog({ events }) {
  const box = useRef(null);
  useEffect(() => {
    if (box.current) box.current.scrollTop = box.current.scrollHeight;
  }, [events.length]);

  return (
    <div className="card stack log-card">
      <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ScrollText size={16} />
        <h3>Bitácora de Simulación</h3>
        <span className="badge mono" style={{ marginLeft: 'auto' }}>{events.length} eventos</span>
      </div>
      <ol className="log" ref={box} aria-live="polite" style={{ flex: 1 }}>
        {events.map((e, i) => {
          const IconComponent = ICONS[e.kind];
          return (
            <li key={i} className={`log-${e.kind}`}>
              <span className="mono font-2xs" style={{ minWidth: '45px', color: '#64748b' }}>
                {e.t.toFixed(1)}s
              </span>
              <span aria-hidden style={{ display: 'inline-flex', alignItems: 'center' }}>
                {IconComponent ? <IconComponent size={13} style={{ marginRight: '4px' }} /> : '·'}
              </span>
              <span>{e.text}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
