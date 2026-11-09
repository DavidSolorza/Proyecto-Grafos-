import React, { useState } from 'react';

export default function MapView({ graphE, graphM }) {
  const [layer, setLayer] = useState('ALL'); // 'ALL' | 'GE' | 'GM'
  const [selectedNode, setSelectedNode] = useState(null);

  const verticesE = graphE?.vertices || [];
  const edgesE = graphE?.edges || [];
  const verticesM = graphM?.vertices || [];
  const corridorsM = graphM?.corridors || [];

  const scale = 5.5;
  const offsetX = 50;
  const offsetY = 50;

  const getPos = (coords) => ({
    x: coords[0] * scale + offsetX,
    y: coords[1] * scale + offsetY,
  });

  return (
    <section style={styles.card}>
      <div style={styles.header}>
        <h2 style={styles.title}>Visualización del Terreno</h2>
        <div style={styles.layerSelector}>
          {['ALL', 'GE', 'GM'].map((m) => (
            <button
              key={m}
              style={{ ...styles.btn, backgroundColor: layer === m ? '#2563eb' : '#f1f5f9', color: layer === m ? '#fff' : '#334155' }}
              onClick={() => setLayer(m)}
            >
              {m === 'ALL' ? 'Ambas Capas' : m === 'GE' ? 'Solo Red GE' : 'Solo Laberinto GM'}
            </button>
          ))}
        </div>
      </div>

      <div style={styles.svgWrapper}>
        <svg width="680" height="340" style={styles.svg}>
          {(layer === 'ALL' || layer === 'GM') && corridorsM.map((c) => {
            const u = verticesM.find((v) => v.id === c.u);
            const v = verticesM.find((v) => v.id === c.v);
            if (!u || !v) return null;
            const p1 = getPos(u.coords);
            const p2 = getPos(v.coords);
            return <line key={c.id} x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y} stroke="#f59e0b" strokeWidth="3" strokeDasharray="4 4" />;
          })}

          {(layer === 'ALL' || layer === 'GE') && edgesE.map((e) => {
            const u = verticesE.find((v) => v.id === e.u);
            const v = verticesE.find((v) => v.id === e.v);
            if (!u || !v) return null;
            const p1 = getPos(u.coords);
            const p2 = getPos(v.coords);
            return <line key={e.id} x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y} stroke="#3b82f6" strokeWidth="2.5" />;
          })}

          {(layer === 'ALL' || layer === 'GM') && verticesM.map((v) => {
            const p = getPos(v.coords);
            const color = v.is_entry ? '#10b981' : v.is_exit ? '#ef4444' : '#d97706';
            return (
              <g key={v.id} onClick={() => setSelectedNode({ ...v, network: 'GM' })} style={{ cursor: 'pointer' }}>
                <rect x={p.x - 7} y={p.y - 7} width="14" height="14" fill={color} stroke="#fff" strokeWidth="1.5" rx="3" />
                <text x={p.x + 9} y={p.y + 4} fontSize="10" fill="#78350f" fontWeight="600">{v.id}</text>
              </g>
            );
          })}

          {(layer === 'ALL' || layer === 'GE') && verticesE.map((v) => {
            const p = getPos(v.coords);
            const color = v.type === 'BASE' ? '#2563eb' : v.type === 'CANDIDATE' ? '#8b5cf6' : '#64748b';
            return (
              <g key={v.id} onClick={() => setSelectedNode({ ...v, network: 'GE' })} style={{ cursor: 'pointer' }}>
                <circle cx={p.x} cy={p.y} r="8" fill={color} stroke="#fff" strokeWidth="2" />
                <text x={p.x + 10} y={p.y + 3} fontSize="11" fill="#1e293b" fontWeight="600">{v.id}</text>
              </g>
            );
          })}
        </svg>
      </div>

      {selectedNode && (
        <div style={styles.detailBox}>
          <strong>Nodo Seleccionado ({selectedNode.network}): </strong>
          <span>ID: {selectedNode.id} | Coords: [{selectedNode.coords.join(', ')}] {selectedNode.z !== undefined ? `| Altura z: ${selectedNode.z}` : ''} {selectedNode.type ? `| Tipo: ${selectedNode.type}` : ''}</span>
          <button style={styles.closeBtn} onClick={() => setSelectedNode(null)}>✕</button>
        </div>
      )}
    </section>
  );
}

const styles = {
  card: { backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '18px 22px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' },
  title: { fontSize: '16px', fontWeight: '600', color: '#1e293b' },
  layerSelector: { display: 'flex', gap: '6px' },
  btn: { padding: '5px 10px', fontSize: '12px', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  svgWrapper: { display: 'flex', justifyContent: 'center', backgroundColor: '#f8fafc', borderRadius: '8px', padding: '10px' },
  svg: { backgroundColor: '#fff', borderRadius: '6px', border: '1px solid #e2e8f0' },
  detailBox: { marginTop: '12px', padding: '8px 14px', backgroundColor: '#eff6ff', borderRadius: '6px', fontSize: '12px', color: '#1e40af', display: 'flex', justifyContent: 'space-between' },
  closeBtn: { background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' },
};
