import React from 'react';

// same colours the map uses
const ITEMS = {
  base: ['#2563eb', 'Base (cuadrado)'],
  candidate: ['#e2e8f0', 'Candidata (rombo)'],
  tower: ['#f59e0b', 'Torre elegida'],
  heliport: ['#0284c7', 'Helipuerto (H)'],
  edge: ['#64748b', 'Camino (GE)'],
  bridge: ['#0284c7', 'Puente (vida)'],
  tree: ['#2563eb', 'Árbol mínimo T_E'],
  corridor: ['#d97706', 'Corredor (GM)'],
  convoy: ['#e11d48', 'Convoy'],
  infantry: ['#38bdf8', 'Infantería'],
  sniper: ['#22c55e', 'Francotirador'],
  gunner: ['#f59e0b', 'Artillero'],
};

/** Small key under the map. Pass the ids of the items that are visible. */
export default function MapLegend({ items }) {
  return (
    <div className="legend">
      {items.map((id) => (
        <span key={id}><i style={{ background: ITEMS[id][0], borderRadius: id === 'candidate' ? 0 : 3 }} />{ITEMS[id][1]}</span>
      ))}
    </div>
  );
}
