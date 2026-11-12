import React from 'react';

/** Shown in every screen that needs data while the app is still empty (requirement §12). */
export default function NoScenario({ loading, onNavigate }) {
  if (loading) return <div className="page">Conectando con el backend…</div>;
  return (
    <div className="page">
      <div className="card stack">
        <h2>Aún no hay un escenario cargado</h2>
        <p>La aplicación arranca vacía: tú eliges el archivo JSON que describe los grafos, el convoy y el presupuesto.</p>
        <button className="btn on start" onClick={() => onNavigate('intro')}>
          Ir a cargar un escenario →
        </button>
      </div>
    </div>
  );
}
