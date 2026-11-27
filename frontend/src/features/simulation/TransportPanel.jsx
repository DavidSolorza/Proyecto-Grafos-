import React, { useState } from 'react';
import { queryPath } from '../../api/client';
import { Send, Compass, Navigation, Plane } from 'lucide-react';

const STATUS = {
  AT_BASE: 'en base',
  STATIONED: 'en torre',
  MOVING: 'en camino',
  WAITING: 'detenido',
  FLYING: 'volando',
  REPAIRING: 'reconstruyendo',
  DEPLOYED: 'en punto',
};
const MODE_NAMES = { walk: 'a pie', moto: 'en moto' };
const TYPES = { INFANTRY: 'Infantería', SNIPER: 'Francotirador', GUNNER: 'Artillero' };
const FREE = ['AT_BASE', 'STATIONED', 'DEPLOYED'];

/** Choose soldiers, a destination and a transport (walk, motorcycle or helicopter). */
export default function TransportPanel({ sim, baseId, vertices, ctrl }) {
  const [picked, setPicked] = useState([]);
  const [dest, setDest] = useState('');
  const [mode, setMode] = useState('walk');
  const [route, setRoute] = useState(null);

  // every GE position is a valid destination; towers and the base come first
  const first = [...sim.towers.map((t) => t.vertex_id), baseId];
  const destinations = [...first, ...vertices.map((v) => v.id).filter((id) => !first.includes(id)).sort()];
  const finished = ['VICTORY_ELIMINATION', 'VICTORY_RESISTANCE', 'DEFEAT'].includes(sim.status);
  const toggle = (id) => {
    setRoute(null);
    setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]));
  };

  const send = async () => {
    const next = mode === 'air' ? await ctrl.fly(picked, dest) : await ctrl.move(picked, dest, mode);
    if (next) setPicked([]);
  };

  const showRoute = async () => {
    const first = sim.soldiers.find((s) => s.id === picked[0]);
    const res = await queryPath(first.vertex, dest, mode === 'moto' ? 'moto' : 'walk');
    setRoute(res.path ? `${res.path.vertices.join(' → ')} (${res.path.time}s)` : 'Sin ruta disponible');
  };

  return (
    <div className="card stack">
      <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Navigation size={16} /> Soldados y Transporte
        </h3>
        <span className="badge mono" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
          <Plane size={13} /> {sim.helicopter.uses_left} usos · ${sim.helicopter.cost}
        </span>
      </div>
      {sim.soldiers.length === 0 ? (
        <p className="note font-sm">Adquiere soldados en el panel de presupuesto para asignarlos a torres.</p>
      ) : (
        <div className="chips">
          {sim.soldiers.map((s) => (
            <label key={s.id} className={`chip ${picked.includes(s.id) ? 'sel' : ''}`}>
              <input
                type="checkbox"
                hidden
                checked={picked.includes(s.id)}
                disabled={!FREE.includes(s.status)}
                onChange={() => toggle(s.id)}
              />
              <b>{s.id} · {TYPES[s.type] ?? s.type}</b>
              <small>{STATUS[s.status]}{FREE.includes(s.status) ? ` ${s.vertex}` : ''}</small>
            </label>
          ))}
        </div>
      )}
      <div className="transport-fields">
        <select value={dest} onChange={(e) => { setDest(e.target.value); setRoute(null); }} aria-label="Destino">
          <option value="">Destino…</option>
          {destinations.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <select value={mode} onChange={(e) => setMode(e.target.value)} aria-label="Medio">
          <option value="walk">A pie (1 soldado)</option>
          <option value="moto">Moto (1 a 2 soldados)</option>
          <option value="air">Helicóptero (hasta 4)</option>
        </select>
      </div>
      <div className="row">
        <button
          className="btn small"
          onClick={send}
          disabled={finished || !picked.length || !dest}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
        >
          <Send size={14} /> Enviar
        </button>
        <button
          className="btn ghost small"
          onClick={showRoute}
          disabled={!picked.length || !dest || mode === 'air'}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
        >
          <Compass size={14} /> Previsualizar ruta
        </button>
      </div>
      {route && <p className="mono route-line">{route}</p>}
      {sim.transfers.map((t) => (
        <p key={t.id} className="mono fine">
          {t.id}: {t.soldiers.join(', ')} → {t.dest} ({t.status === 'WAITING' ? 'detenido por puente' : MODE_NAMES[t.mode] ?? t.mode})
        </p>
      ))}
    </div>
  );
}
