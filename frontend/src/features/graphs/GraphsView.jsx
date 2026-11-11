import React, { useState } from 'react';
import GraphMap from '../map/GraphMap';
import MapLegend from '../../components/MapLegend';
import NodeInfo from '../../components/NodeInfo';
import Explainer from '../../components/Explainer';

const MODES = [
  ['both', 'Ambas capas'],
  ['ge', 'Red elevada GE'],
  ['gm', 'Laberinto GM'],
];

/** Shows the scenario graphs before any planning, so the structure is clear. */
export default function GraphsView({ scenario }) {
  const [mode, setMode] = useState('both');
  const [selected, setSelected] = useState(null);

  const layers = { ge: mode !== 'gm', gm: mode !== 'ge', tree: false, radii: false };
  return (
    <div className="page">
      <header className="page-head">
        <p className="eyebrow">Modelo de datos</p>
        <h2>Dos grafos que comparten el mismo plano</h2>
        <p>
          No hay aristas entre ambos: solo se relacionan por la distancia. Un soldado en la red elevada
          puede disparar a un robot que camina por el laberinto si está dentro de su alcance.
        </p>
      </header>

      <div className="grid-2">
        <div>
          <div className="toolbar">
            {MODES.map(([id, label]) => (
              <button key={id} className={`btn small ${mode === id ? 'on' : 'ghost'}`} onClick={() => setMode(id)}>
                {label}
              </button>
            ))}
          </div>
          <GraphMap graphE={scenario.graph_e} graphM={scenario.graph_m} layers={layers}
            selected={selected} onSelect={setSelected} />
          <MapLegend items={['base', 'candidate', 'heliport', 'edge', 'corridor']} />
        </div>

        <div className="stack">
          <NodeInfo node={selected} onClose={() => setSelected(null)} />
          <Explainer title="¿Cómo se guarda un grafo aquí?" open>
            <p>
              Cada grafo es una clase con dos diccionarios: <code>vertices</code> (id → vértice) y
              <code> adj</code> (id → lista de aristas). Para recorrer los vecinos de un vértice basta
              mirar <code>adj[id]</code>.
            </p>
            <p>Agregar un vértice o una arista cuesta O(1); comprobar si dos vértices están unidos, O(grado).</p>
          </Explainer>
          <Explainer title="¿Qué es la componente conexa de la base?">
            <p>
              Es el conjunto de posiciones a las que se puede llegar caminando desde la base. Una torre solo
              puede ubicarse ahí. Se calcula con un BFS que ignora los puentes destruidos.
            </p>
            <p className="formula">{scenario.graph_e.connected_component_base.length} de {scenario.graph_e.vertices.length} vértices alcanzables</p>
          </Explainer>
        </div>
      </div>
    </div>
  );
}
