import React from 'react';
import { ShieldAlert, Heart, HelpCircle } from 'lucide-react';

const NAMES = { TANK: 'Tanque', TRUCK: 'Camión', ROBOT_SOLDIER: 'Soldado robot' };

/** Health of every machine and the explanation of the last route decision. */
export default function ConvoyPanel({ sim }) {
  const d = sim.convoy.decision;
  return (
    <div className="card stack">
      <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ShieldAlert size={16} color="#d97706" />
        <h3>Convoy Enemigo</h3>
      </div>
      <div className="foes">
        {sim.convoy.enemies.map((e) => (
          <div key={e.id} className={`foe ${e.alive ? '' : 'dead'}`}>
            <b>{e.id}</b>
            <span>{NAMES[e.type]}</span>
            <span className="mono">
              <Heart size={12} color={e.alive ? '#dc2626' : '#94a3b8'} aria-hidden /> {e.hp}/{e.max_hp} HP
            </span>
            <div className="bar red"><i style={{ width: `${(e.hp / e.max_hp) * 100}%` }} /></div>
          </div>
        ))}
      </div>
      {d && (
        <>
          <h3 className="mt-s" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <HelpCircle size={15} /> ¿Por qué eligió ese camino?
          </h3>
          <p className="note">En <b>{d.at}</b> (t = {d.time}s): {d.note}.</p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Corredor</th>
                  <th>Hacia</th>
                  <th>Costo (w + resto)</th>
                </tr>
              </thead>
              <tbody>
                {d.options.map((o) => (
                  <tr key={o.corridor} className={o.corridor === d.chosen.corridor ? 'picked' : ''}>
                    <td><b>{o.corridor}</b></td>
                    <td>{o.to}</td>
                    <td className="num">{o.cost.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Corredor</th>
              <th>t(e)</th>
              <th>Peligro P(e)</th>
              <th>Peso w(e)</th>
            </tr>
          </thead>
          <tbody>
            {sim.corridors.map((c) => (
              <tr key={c.id}>
                <td><b>{c.id}</b></td>
                <td className="num">{c.time.toFixed(1)}</td>
                <td className="num">{c.danger.toFixed(1)}</td>
                <td className="num" style={{ fontWeight: '600', color: c.danger > 0 ? '#b45309' : 'inherit' }}>
                  {c.weight.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="fine">w(e) = t(e) + α · P(e). Se recalcula en cada intersección según las defensas activas.</p>
    </div>
  );
}
