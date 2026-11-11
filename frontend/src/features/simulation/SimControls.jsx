import React from 'react';

const STATUS = {
  IDLE: ['Listo', ''],
  RUNNING: ['En combate', 'warn'],
  VICTORY_ELIMINATION: ['Victoria por eliminación', 'ok'],
  VICTORY_RESISTANCE: ['Victoria por resistencia', 'ok'],
  DEFEAT: ['Derrota', 'bad'],
};

/** Play / pause / step / speed buttons and the logical clock. */
export default function SimControls({ sim, ctrl }) {
  const [label, tone] = STATUS[sim.status] ?? [sim.status, ''];
  const pct = Math.min(100, (sim.clock / sim.time_limit) * 100);
  return (
    <div className="card stack">
      <div className="row spread">
        <span className={`badge ${tone}`}>{label}</span>
        <span className="mono">{sim.clock.toFixed(1)}s / {sim.time_limit}s</span>
      </div>
      <div className="bar" aria-hidden><i style={{ width: `${pct}%` }} /></div>
      <div className="row">
        <button className="btn small" onClick={ctrl.togglePlay} disabled={ctrl.finished}>
          {ctrl.running ? '❚❚ Pausar' : '▶ Iniciar'}
        </button>
        <button className="btn ghost small" onClick={ctrl.step} disabled={ctrl.running || ctrl.finished}>+1 s</button>
        {[1, 2, 5].map((n) => (
          <button key={n} className={`btn small ${ctrl.speed === n ? 'on' : 'ghost'}`} onClick={() => ctrl.setSpeed(n)}>{n}×</button>
        ))}
        <button className="btn ghost small" onClick={ctrl.reset}>↺ Reiniciar</button>
      </div>
    </div>
  );
}
