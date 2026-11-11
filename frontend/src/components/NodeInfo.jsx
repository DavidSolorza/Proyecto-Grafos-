import React from 'react';
import { typeLabel } from '../features/map/NodeLayer';

/** Details of the vertex the user clicked on the map. */
export default function NodeInfo({ node, onClose }) {
  if (!node) {
    return <p className="node-info">Haz clic en un vértice del mapa para ver sus datos.</p>;
  }
  const kind = node.network === 'GE'
    ? `Red elevada · ${typeLabel(node.type)} · altura z = ${node.z}`
    : `Laberinto · ${node.is_entry ? 'entrada' : node.is_exit ? 'salida' : 'intersección'}`;
  return (
    <div className="node-info card">
      <div>
        <b>{node.id}</b>
        <div className="mono">{kind} · coords ({node.coords.join(', ')})</div>
      </div>
      <button className="btn ghost small" onClick={onClose} aria-label="Cerrar">Cerrar</button>
    </div>
  );
}
