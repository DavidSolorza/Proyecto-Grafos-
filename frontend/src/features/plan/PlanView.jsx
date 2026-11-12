import React, { useState } from 'react';
import GraphMap from '../map/GraphMap';
import MapLegend from '../../components/MapLegend';
import Explainer from '../../components/Explainer';
import PlanSteps from './PlanSteps';

export default function PlanView({ scenario, plan, onCalculate, error, onNavigate }) {
  const [showTree, setShowTree] = useState(true);
  const [showRadii, setShowRadii] = useState(true);
  const [busy, setBusy] = useState(false);

  const calculate = async () => {
    setBusy(true);
    await onCalculate();
    setBusy(false);
  };
  const layers = { ge: true, gm: true, tree: showTree && !!plan, radii: showRadii && !!plan };

  return (
    <div className="page">
      <header className="page-head">
        <p className="eyebrow">Fase 1 · Antes del combate</p>
        <h2>Plan de defensa</h2>
        <p>
          Primero se construye el árbol de expansión mínima sobre lo que la base puede alcanzar. Luego se eligen
          hasta K torres: las que vigilan más corredores sin quedar demasiado lejos de la base.
        </p>
      </header>

      <div className="grid-2">
        <div className="sticky-col">
          <div className="toolbar">
            <button className="btn small" onClick={calculate} disabled={busy}>
              {busy ? 'Calculando…' : plan ? 'Recalcular plan' : 'Calcular plan'}
            </button>
            <button className={`btn small ${showTree ? 'on' : 'ghost'}`} onClick={() => setShowTree(!showTree)} disabled={!plan}>Árbol T_E</button>
            <button className={`btn small ${showRadii ? 'on' : 'ghost'}`} onClick={() => setShowRadii(!showRadii)} disabled={!plan}>Radios Rv</button>
          </div>
          {error && <div className="alert error mb-m">{error}</div>}
          <GraphMap graphE={scenario.graph_e} graphM={scenario.graph_m} plan={plan} layers={layers} />
          <MapLegend items={['base', 'tower', 'tree', 'corridor']} />
        </div>

        <div className="stack">
          {!plan && <div className="card"><p>Pulsa <b>Calcular plan</b> para ver el árbol, las torres y la cobertura.</p></div>}
          {plan && (
            <>
              <div className="card stack">
                <div className="stats">
                  <div className="stat"><b>{plan.towers.length}</b><span>Torres</span></div>
                  <div className="stat"><b>{plan.coverage_pct}%</b><span>Cobertura</span></div>
                  <div className="stat"><b>{plan.mst.total_time}s</b><span>Peso del MST</span></div>
                  <div className="stat"><b>{plan.mst.edges.length}</b><span>Aristas T_E</span></div>
                </div>
                <p className="note">
                  Corredores vigilados: <b>{plan.covered_corridors.length} de {scenario.graph_m.corridors.length}</b>{' '}
                  ({plan.covered_length} de {plan.total_length} u. de longitud): {plan.covered_corridors.join(', ') || 'ninguno'}.
                </p>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Torre</th><th>Rv</th><th>D_T</th><th>S(p)</th></tr></thead>
                    <tbody>
                      {plan.towers.map((t) => (
                        <tr key={t.vertex_id}>
                          <td>{t.vertex_id}</td><td className="num">{t.rv}</td>
                          <td className="num">{t.dt.toFixed(1)}s</td><td className="num">{t.score.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {plan.unreachable.length > 0 && (
                  <p className="alert">Fuera de la componente de la base (no pueden ser torres): {plan.unreachable.join(', ')}</p>
                )}
                <button className="btn" onClick={() => onNavigate('sim')}>Ir a la simulación →</button>
              </div>

              <Explainer title="Paso a paso de la selección voraz" open>
                <PlanSteps steps={plan.steps} />
              </Explainer>
            </>
          )}

          <Explainer title="¿Qué calcula la puntuación S(p)?">
            <p className="formula">S(p) = C(p) / (1 + D_T(B,p) / D₀)</p>
            <p><b>C(p)</b>: longitud de corredores aún sin vigilar dentro del radio Rv (se mide hasta el punto medio).</p>
            <p><b>D_T(B,p)</b>: tiempo a pie de la base a p siguiendo solo el árbol. <b>D₀</b>: tiempo de referencia ({scenario.metadata.d0}s).</p>
            <p>Empates: menor D_T y luego el id en orden alfabético.</p>
          </Explainer>
          <Explainer title="¿Cómo funciona Kruskal?">
            <p>1) Ordena las aristas por tiempo a pie. 2) Recorre la lista y acepta una arista solo si une dos componentes distintas (Union-Find). 3) Termina con V−1 aristas.</p>
            <p>El árbol es solo una referencia: <b>no elimina</b> las demás aristas del grafo.</p>
          </Explainer>
        </div>
      </div>
    </div>
  );
}
