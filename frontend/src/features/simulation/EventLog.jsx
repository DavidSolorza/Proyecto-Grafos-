import React, { useEffect, useRef } from 'react';

const ICON = { combat: '⚔', convoy: '▶', bridge: '⌇', move: '→', air: '✚', buy: '$', end: '■', system: '·' };

/** Explains what happened and why. Newest events at the bottom, auto-scrolled. */
export default function EventLog({ events }) {
  const box = useRef(null);
  useEffect(() => {
    if (box.current) box.current.scrollTop = box.current.scrollHeight;
  }, [events.length]);

  return (
    <div className="card dark">
      <div className="card-title"><h3>Bitácora</h3><span className="mono">{events.length} eventos</span></div>
      <ol className="log" ref={box} aria-live="polite">
        {events.map((e, i) => (
          <li key={i} className={`log-${e.kind}`}>
            <span className="mono">{e.t.toFixed(1)}s</span>
            <span aria-hidden>{ICON[e.kind] ?? '·'}</span>
            <span>{e.text}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
