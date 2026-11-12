import React, { useState } from 'react';
import { queryPath } from '../../api/client';

const STATUS = { AT_BASE: 'en base', STATIONED: 'en torre', MOVING: 'en camino', WAITING: 'detenido', FLYING: 'volando', REPAIRING: 'reconstruyendo' };
const FREE = ['AT_BASE', 'STATIONED'];

/** Choose soldiers, a destination and a transport (walk, motorcycle or helicopter). */
export default function TransportPanel({ sim, baseId, ctrl }) {
  const [picked, setPicked] = useState([]);
  const [dest, setDest] = useState('');
  const [mode, setMode] = useState('walk');
  const [route, setRoute] = useState(null);

  const destinations = [...sim.towers.map((t) => t.vertex_id), baseId];
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
      <div className="card-title">
        <h3>Soldados y transporte</h3>
        <span className="badge mono">helicópteros: {sim.helicopter.uses_left} · ${sim.helicopter.cost}</span>
      </div>
      {sim.soldiers.length === 0 ? <p>Compra un soldado para poder moverlo.</p> : (
        <div className="chips">
          {sim.soldiers.map((s) => (
            <label key={s.id} className={`chip ${picked.includes(s.id) ? 'sel' : ''}`}>
              <input type="checkbox" hidden checked={picked.includes(s.id)} disabled={!FREE.includes(s.status)}
                onChange={() => toggle(s.id)} />
              <b>{s.id}</b> {s.type.slice(0, 3)} · {STATUS[s.status]}{FREE.includes(s.status) ? ` ${s.vertex}` : ''}
            </label>
          ))}
        </div>
      )}
      <div className="row">
        <select value={dest} onChange={(e) => { setDest(e.target.value); setRoute(null); }} aria-label="Destino">
          <option value="">Destino…</option>
          {destinations.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
        <select value={mode} onChange={(e) => setMode(e.target.value)} aria-label="Medio">
          <option value="walk">A pie (1)</option>
          <option value="moto">Moto (1–2)</option>
          <option value="air">Helicóptero (hasta 4)</option>
        </select>
      </div>
      <div className="row">
        <button className="btn small" onClick={send} disabled={!picked.length || !dest}>Enviar</button>
        <button className="btn ghost small" onClick={showRoute} disabled={!picked.length || !dest || mode === 'air'}>Ver ruta</button>
      </div>
      {route && <p className="mono route-line">{route}</p>}
      {sim.transfers.map((t) => (
        <p key={t.id} className="mono fine">
          {t.id}: {t.soldiers.join(', ')} → {t.dest} ({t.status === 'WAITING' ? 'detenido, esperando ruta' : t.mode})
        </p>
      ))}
    </div>
  );
}
