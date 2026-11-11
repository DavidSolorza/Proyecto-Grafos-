import React from 'react';

const NAMES = { TANK: 'Tanque', TRUCK: 'Camión', ROBOT_SOLDIER: 'Soldado robot' };

/** Health of every machine and the explanation of the last route decision. */
export default function ConvoyPanel({ sim }) {
  const d = sim.convoy.decision;
  return (
    <div className="card stack">
      <div className="card-title"><h3>Convoy enemigo</h3></div>
      {sim.convoy.enemies.map((e) => (
        <div key={e.id} className={`enemy ${e.alive ? '' : 'dead'}`}>
          <div className="row spread"><span>{e.id} · {NAMES[e.type]}</span><span className="mono">{e.hp}/{e.max_hp} HP</span></div>
          <div className="bar red"><i style={{ width: `${(e.hp / e.max_hp) * 100}%` }} /></div>
        </div>
      ))}
      {d && (
        <>
          <h3 style={{ marginTop: 6 }}>¿Por qué ese camino?</h3>
          <p style={{ fontSize: '0.85rem' }}>En <b>{d.at}</b> (t = {d.time}s): {d.note}.</p>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Corredor</th><th>Hacia</th><th>w + resto</th></tr></thead>
              <tbody>
                {d.options.map((o) => (
                  <tr key={o.corridor} className={o.corridor === d.chosen.corridor ? 'picked' : ''}>
                    <td>{o.corridor}</td><td>{o.to}</td><td className="num">{o.cost.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      <div className="table-wrap">
        <table>
          <thead><tr><th>Corredor</th><th>t(e)</th><th>P(e)</th><th>w(e)</th></tr></thead>
          <tbody>
            {sim.corridors.map((c) => (
              <tr key={c.id}>
                <td>{c.id}</td><td className="num">{c.time.toFixed(1)}</td>
                <td className="num">{c.danger.toFixed(1)}</td><td className="num">{c.weight.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p style={{ fontSize: '0.78rem' }}>w(e) = t(e) + α · P(e). Se recalcula en cada intersección con las defensas activas.</p>
    </div>
  );
}
