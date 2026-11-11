import React from 'react';

const NAMES = { infantry: 'Infantería', sniper: 'Francotirador', gunner: 'Artillero' };

/** Budget (available / reserved) and the buttons to buy soldiers. They appear at the base. */
export default function RecruitPanel({ sim, onRecruit }) {
  const { budget, defenders_config: cfg } = sim;
  return (
    <div className="card stack">
      <div className="card-title"><h3>Presupuesto</h3></div>
      <div className="stats">
        <div className="stat"><b>${budget.available.toFixed(0)}</b><span>Disponible</span></div>
        <div className="stat"><b>${budget.reserved.toFixed(0)}</b><span>Reservado</span></div>
        <div className="stat"><b>${budget.earned.toFixed(0)}</b><span>Recompensas</span></div>
      </div>
      <div className="recruit">
        {Object.entries(cfg).sort((a, b) => a[1].cost - b[1].cost).map(([type, c]) => (
          <button key={type} className="btn ghost small recruit-btn" onClick={() => onRecruit(type, 1)}
            disabled={budget.available < c.cost}>
            <b>{NAMES[type] ?? type}</b>
            <span>${c.cost} · daño {c.damage} · alcance {c.base_range} · {c.frequency}/s</span>
          </button>
        ))}
      </div>
    </div>
  );
}
