import React from 'react';

export const TABS = [
  { id: 'intro', n: '01', label: 'Inicio' },
  { id: 'graphs', n: '02', label: 'Los grafos' },
  { id: 'plan', n: '03', label: 'Plan de defensa' },
  { id: 'sim', n: '04', label: 'Simulación' },
];

/** Black top bar with the project name, backend status and navigation tabs. */
export default function Header({ active, onChange, isConnected }) {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <h1>
            General P. Tardo
            <small>Simulador de grafos · Estructuras de Datos</small>
          </h1>
          <div className="status-pill" title="Estado de la conexión con Flask">
            <span className={`dot ${isConnected ? 'on' : ''}`} />
            {isConnected ? 'Backend conectado' : 'Backend sin conexión'}
          </div>
        </div>
        <nav className="tabs" aria-label="Secciones">
          {TABS.map((t) => (
            <button key={t.id} className={`tab ${active === t.id ? 'active' : ''}`}
              onClick={() => onChange(t.id)} aria-current={active === t.id ? 'page' : undefined}>
              <span>{t.n}</span>{t.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}
