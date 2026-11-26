import React from 'react';
import { DollarSign, Shield, Crosshair, Flame } from 'lucide-react';

const ICONS = {
  infantry: Shield,
  sniper: Crosshair,
  gunner: Flame,
};

const NAMES = { infantry: 'Infantería', sniper: 'Francotirador', gunner: 'Artillero' };

/** Budget (available / reserved) and the buttons to buy soldiers. They appear at the base. */
export default function RecruitPanel({ sim, onRecruit }) {
  const { budget, defenders_config: cfg } = sim;
  return (
    <div className="card stack">
      <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <DollarSign size={16} />
        <h3>Presupuesto y Reclutamiento</h3>
      </div>
      <div className="stats">
        <div className="stat">
          <b>${budget.available.toFixed(0)}</b>
          <span>Disponible</span>
        </div>
        <div className="stat">
          <b>${budget.reserved.toFixed(0)}</b>
          <span>Reservado</span>
        </div>
        <div className="stat" style={{ color: '#059669' }}>
          <b>+${budget.earned.toFixed(0)}</b>
          <span>Bajas enemigas</span>
        </div>
      </div>
      <div className="recruit">
        {Object.entries(cfg).sort((a, b) => a[1].cost - b[1].cost).map(([type, c]) => {
          const Icon = ICONS[type] || Shield;
          return (
            <button
              key={type}
              className="btn ghost small recruit-btn"
              onClick={() => onRecruit(type, 1)}
              disabled={budget.available < c.cost}
              style={{ display: 'flex', alignItems: 'center', gap: '10px', textAlign: 'left' }}
            >
              <Icon size={18} style={{ flexShrink: 0, opacity: 0.8 }} />
              <div style={{ flex: 1 }}>
                <b>{NAMES[type] ?? type} (${c.cost})</b>
                <div className="font-2xs" style={{ opacity: 0.75 }}>
                  Daño: {c.damage} · Alcance: {c.base_range} · {c.frequency}/s
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
