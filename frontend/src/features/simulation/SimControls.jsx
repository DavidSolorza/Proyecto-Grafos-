import React from 'react';
import { Play, Pause, RotateCcw, StepForward, Clock, Zap } from 'lucide-react';

const STATUS = {
  IDLE: ['Listo para iniciar', ''],
  RUNNING: ['Combate en curso', 'warn'],
  VICTORY_ELIMINATION: ['¡Victoria por eliminación!', 'ok'],
  VICTORY_RESISTANCE: ['¡Victoria por resistencia (300s)!', 'ok'],
  DEFEAT: ['Derrota: El convoy escapó', 'bad'],
};

/** Play / pause / step / speed buttons and the logical clock. */
export default function SimControls({ sim, ctrl }) {
  const [label, tone] = STATUS[sim.status] ?? [sim.status, ''];
  const pct = Math.min(100, (sim.clock / sim.time_limit) * 100);

  return (
    <div className="card stack">
      <div className="row spread" style={{ alignItems: 'center' }}>
        <span className={`badge ${tone}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={13} />
          {label}
        </span>
        <span className="mono" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Clock size={14} style={{ opacity: 0.7 }} />
          {sim.clock.toFixed(1)}s / {sim.time_limit}s
        </span>
      </div>
      <div className="bar" aria-hidden><i style={{ width: `${pct}%` }} /></div>
      <div className="row" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <button
          className={`btn small ${ctrl.running ? 'btn-danger' : 'btn-primary'}`}
          onClick={ctrl.togglePlay}
          disabled={ctrl.finished}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
        >
          {ctrl.running ? <Pause size={14} /> : <Play size={14} />}
          {ctrl.running ? 'Pausar' : 'Iniciar'}
        </button>
        <button
          className="btn ghost small"
          onClick={ctrl.step}
          disabled={ctrl.running || ctrl.finished}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
        >
          <StepForward size={14} />
          +1s
        </button>
        <div style={{ display: 'inline-flex', gap: '4px' }}>
          {[1, 2, 5].map((n) => (
            <button
              key={n}
              className={`btn small ${ctrl.speed === n ? 'on' : 'ghost'}`}
              onClick={() => ctrl.setSpeed(n)}
            >
              {n}×
            </button>
          ))}
        </div>
        <button
          className="btn ghost small"
          onClick={ctrl.reset}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', marginLeft: 'auto' }}
        >
          <RotateCcw size={14} />
          Reiniciar
        </button>
      </div>
    </div>
  );
}
