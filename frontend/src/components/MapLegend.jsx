import React from 'react';

const ITEMS = {
  base: ['#f0e7d6', 'Base (cuadrado)'],
  candidate: ['#8a7a5c', 'Candidata (rombo)'],
  tower: ['#d9a441', 'Torre elegida'],
  heliport: ['#a89c84', 'Helipuerto (H)'],
  edge: ['#e8dcc4', 'Camino / puente (GE)'],
  tree: ['#8fb27c', 'Árbol mínimo T_E'],
  corridor: ['#c7704f', 'Corredor (GM)'],
  convoy: ['#e0533a', 'Convoy'],
  soldier: ['#8fb27c', 'Soldado'],
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
