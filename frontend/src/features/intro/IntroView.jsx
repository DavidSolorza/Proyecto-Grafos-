import React from 'react';
import FileUploader from '../../components/FileUploader';
import ScenarioSummary from '../../components/ScenarioSummary';
import '../../styles/intro.css';

const STEPS = [
  ['01', 'Carga el escenario', 'Un JSON describe los dos grafos, el convoy y el presupuesto. El backend valida que sea coherente.', 'intro'],
  ['02', 'Planifica la defensa', 'Kruskal arma el árbol mínimo y un algoritmo voraz elige dónde ubicar las torres.', 'plan'],
  ['03', 'Simula el combate', 'Compra soldados, envíalos por tierra o aire y mira cómo el convoy esquiva el peligro.', 'sim'],
];

// What each algorithm does and what it costs (V = vertices, E = edges)
const CONCEPTS = [
  ['Lista de adyacencia', 'Cada vértice guarda sus aristas. Ahorra memoria en grafos con pocas conexiones.', 'O(V + E) memoria'],
  ['BFS · componente conexa', 'Recorre por capas desde la base para saber qué posiciones son alcanzables.', 'O(V + E)'],
  ['Kruskal + Union-Find', 'Ordena las aristas por tiempo a pie y une componentes sin crear ciclos.', 'O(E log E)'],
  ['Dijkstra', 'Camino más barato. Lo usan los soldados (tiempo) y el convoy (tiempo + peligro).', 'O((V + E) log V)'],
  ['Voraz (greedy)', 'Cada ronda elige la torre con mejor puntaje S(p) y recalcula lo que queda sin cubrir.', 'O(K · C · M)'],
  ['Reloj lógico', 'La simulación avanza en pasos de 0,25 s, sin depender de los fotogramas del navegador.', 'O(unidades) por paso'],
];

export default function IntroView({ scenario, validation, onReload, onNavigate, error, loading }) {
  return (
    <div className="page">
      <section className="hero">
        <p className="eyebrow">Proyecto 2 · Grafos</p>
        <h2>La derrota del dictador General P. Tardo</h2>
        <p>
          Un convoy de máquinas avanza por un laberinto (grafo <b>GM</b>) hacia la salida. Los humanos
          resisten desde una red elevada de caminos y puentes (grafo <b>GE</b>). Tú decides dónde
          construir las torres y a quién enviar a cada una.
        </p>
        {scenario
          ? <button className="btn on" onClick={() => onNavigate('plan')}>Empezar por el plan →</button>
          : <p className="hint">Para empezar, carga un escenario JSON en el recuadro de abajo.</p>}
      </section>

      <section className="steps">
        {STEPS.map(([n, title, text, target]) => (
          <button key={n} className="step" onClick={() => onNavigate(target)}>
            <span className="mono">{n}</span>
            <h3>{title}</h3>
            <p>{text}</p>
          </button>
        ))}
      </section>

      {error && <div className="alert error">{error}</div>}

      <section className="grid-2 mt-m">
        {scenario
          ? <ScenarioSummary scenario={scenario} validation={validation} />
          : <div className="card stack">
              <h3>{loading ? 'Conectando con el backend…' : 'Sin escenario cargado'}</h3>
              {!loading && <p>La aplicación arranca vacía. Aquí aparecerá el resumen cuando subas un archivo.</p>}
            </div>}
        <FileUploader onUploaded={onReload} />
      </section>

      <section className="mt-l">
        <h2 className="mb-m">Estructuras y algoritmos del proyecto</h2>
        <div className="concepts">
          {CONCEPTS.map(([name, text, cost]) => (
            <article key={name} className="card concept">
              <h3>{name}</h3>
              <p>{text}</p>
              <span className="badge warn mono">{cost}</span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
