import React, { useEffect, useState } from 'react';
import GraphMap from '../map/GraphMap';
import MapLegend from '../../components/MapLegend';
import NodeInfo from '../../components/NodeInfo';
import SimControls from './SimControls';
import RecruitPanel from './RecruitPanel';
import TransportPanel from './TransportPanel';
import ConvoyPanel from './ConvoyPanel';
import EventLog from './EventLog';
import '../../styles/sim.css';

const END = {
  VICTORY_ELIMINATION: ['win', 'Victoria por eliminación'],
  VICTORY_RESISTANCE: ['win', 'Victoria por resistencia'],
  DEFEAT: ['lose', 'Derrota'],
};

export default function SimView({ scenario, plan, ctrl, onNavigate }) {
  const [selected, setSelected] = useState(null);
  const [hideEnd, setHideEnd] = useState(false); // lets the user look at the final map
  const { state: sim } = ctrl;
  const finished = ctrl.finished;
  useEffect(() => { if (!finished) setHideEnd(false); }, [finished]); // new match -> banner again

  if (!plan) {
    return (
      <div className="page"><div className="card stack">
        <h2>Primero el plan</h2>
        <p>La simulación necesita las torres elegidas por el árbol mínimo y el algoritmo voraz.</p>
        <button className="btn start" onClick={() => onNavigate('plan')}>Calcular plan →</button>
      </div></div>
    );
  }
  if (!sim) {
    return (
      <div className="page"><div className="card stack">
        <h2>Todo listo para el combate</h2>
        <p>Se crea una partida nueva con las {plan.towers.length} torres del plan. Después no se pueden mover.</p>
        {ctrl.error && <div className="alert error">{ctrl.error}</div>}
        <button className="btn start" onClick={ctrl.reset}>Crear simulación</button>
      </div></div>
    );
  }

  const base = scenario.graph_e.vertices.find((v) => v.type === 'BASE');
  const end = END[sim.status];
  return (
    <div className="page">
      <header className="page-head">
        <p className="eyebrow">Fase 2 · Combate en tiempo lógico</p>
        <h2>Simulación</h2>
      </header>
      {ctrl.error && (
        <div className="alert error mb-m" role="alert">
          {ctrl.error} <button className="btn ghost small" onClick={ctrl.clearError}>Cerrar</button>
        </div>
      )}
      <div className="grid-2">
        <div className="stack sticky-col">
          <GraphMap graphE={scenario.graph_e} graphM={scenario.graph_m} plan={plan} sim={sim}
            layers={{ ge: true, gm: true, tree: false, radii: false }} selected={selected} onSelect={setSelected}>
            {end && !hideEnd && (
              <div className={`end-banner ${end[0]}`} role="status">
                <h2>{end[1]}</h2><p>{sim.end_reason}</p>
                <div className="row center">
                  <button className="btn on" onClick={() => { setHideEnd(false); ctrl.reset(); }}>Jugar de nuevo</button>
                  <button className="btn ghost small light" onClick={() => setHideEnd(true)}>Ver mapa</button>
                </div>
              </div>
            )}
          </GraphMap>
          <MapLegend items={['base', 'tower', 'edge', 'corridor', 'convoy', 'soldier']} />
          <NodeInfo node={selected} onClose={() => setSelected(null)} />
        </div>
        <div className="stack">
          <SimControls sim={sim} ctrl={ctrl} />
          <RecruitPanel sim={sim} onRecruit={ctrl.recruit} />
          <TransportPanel sim={sim} baseId={base.id} ctrl={ctrl} />
          <ConvoyPanel sim={sim} />
          <EventLog events={sim.events} />
        </div>
      </div>
    </div>
  );
}
