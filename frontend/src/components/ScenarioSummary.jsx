import React from 'react';

const CHECKS = [
  ['has_base', 'Exactamente una base'],
  ['base_connected', 'La base tiene componente conexa'],
  ['labyrinth_path_exists', 'Existe camino entrada → salida'],
];

/** Scenario parameters and the invariants the backend verified. */
export default function ScenarioSummary({ scenario, validation }) {
  const m = scenario.metadata;
  const stats = [
    [`$${m.initial_budget}`, 'Presupuesto'],
    [m.max_towers_k, 'Torres máx. (K)'],
    [`${m.d0}s`, 'Tiempo ref. D₀'],
    [m.alpha, 'Peligro α'],
    [m.beta, 'Altura β'],
    [`${m.bridge_repair_time}s`, 'Reparar puente'],
    [m.bridge_repair_crew ?? 0, 'Personas por reparación'],
  ];
  const c = scenario.convoy;
  return (
    <div className="card stack">
      <div className="card-title">
        <h3>{m.title}</h3>
        <span className="badge ok">escenario activo</span>
      </div>
      <div className="stats">
        {stats.map(([value, label]) => (
          <div className="stat" key={label}><b>{value}</b><span>{label}</span></div>
        ))}
      </div>
      <p style={{ fontSize: '0.88rem' }}>
        Convoy enemigo: <b>{c.tanks}</b> tanque(s), <b>{c.trucks}</b> camión(es) y{' '}
        <b>{c.robot_soldiers}</b> soldado(s) robot. Grafo GE: {scenario.graph_e.vertices.length} vértices y{' '}
        {scenario.graph_e.edges.length} aristas. Grafo GM: {scenario.graph_m.vertices.length} vértices y{' '}
        {scenario.graph_m.corridors.length} corredores.
      </p>
      {validation && (
        <ul className="row" style={{ listStyle: 'none', gap: 8 }}>
          {CHECKS.map(([key, label]) => (
            <li key={key} className={`badge ${validation[key] ? 'ok' : 'bad'}`}>
              {validation[key] ? '✓' : '✗'} {label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
