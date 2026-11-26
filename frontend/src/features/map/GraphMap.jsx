import React, { useState } from 'react';
import { computeView } from './mapGeometry';
import { CorridorLayer, EdgeLayer, RadiusLayer } from './MapLayers';
import { NodeLayer } from './NodeLayer';
import SimOverlay from './SimOverlay';
import CombatEffectsLayer from './CombatEffectsLayer';
import MapHud from './MapHud';
import NodePopover from './NodePopover';
import '../../styles/map.css';

/** Responsive SVG battlefield. Draws terrain corridors, elevated walkways, units, and HUD. */
export default function GraphMap({
  graphE, graphM, plan, sim, layers: initialLayers = { ge: true, gm: true, tree: false, radii: false },
  selected, onSelect = () => {}, onRecruit, children, routeIds = [],
}) {
  const [layers, setLayers] = useState(initialLayers);
  if (!graphE || !graphM) return null;
  const view = computeView(graphE, graphM);
  const towerIds = sim ? sim.towers.map((t) => t.vertex_id) : (plan?.towers ?? []).map((t) => t.vertex_id);
  const towerPoints = sim
    ? sim.towers
    : (plan?.towers ?? []).map((t) => ({ ...t, xy: graphE.vertices.find((v) => v.id === t.vertex_id)?.coords }));

  const toggleLayer = (k) => setLayers((prev) => ({ ...prev, [k]: !prev[k] }));

  return (
    <div className="stage tactical-stage">
      <MapHud sim={sim} layers={layers} onToggleLayer={toggleLayer} hasPlan={!!plan} />
      <svg viewBox={`${view.minX} ${view.minY} ${view.w} ${view.h}`} role="img"
        aria-label="Mapa de batalla táctico: red elevada GE y laberinto GM" preserveAspectRatio="xMidYMid meet">
        <defs>
          <pattern id="tac-grid" width={view.u * 8} height={view.u * 8} patternUnits="userSpaceOnUse">
            <path d={`M ${view.u * 8} 0 L 0 0 0 ${view.u * 8}`} fill="none" stroke="rgba(148, 163, 184, 0.22)" strokeWidth={view.u * 0.15} />
          </pattern>
          <filter id="node-shadow" x="-30%" y="-30%" width="160%" height="160%">
            <feDropShadow dx="0" dy="1.5" stdDeviation="1" floodColor="#0f172a" floodOpacity="0.25" />
          </filter>
        </defs>
        <rect x={view.minX} y={view.minY} width={view.w} height={view.h} fill="url(#tac-grid)" />
        {layers.radii && towerPoints.length > 0 && <RadiusLayer towers={towerPoints} view={view} />}
        {layers.gm && (
          <CorridorLayer graphM={graphM} view={view} simCorridors={sim?.corridors} routeIds={routeIds}
            covered={plan?.covered_corridors} showCoverage={layers.tree && !sim} />
        )}
        {layers.ge && (
          <EdgeLayer graphE={graphE} view={view} bridges={sim?.bridges}
            treeIds={plan?.mst.edges.map((e) => e.id)} showTree={layers.tree && !sim} />
        )}
        <NodeLayer graphE={graphE} graphM={graphM} view={view} showE={layers.ge} showM={layers.gm}
          towerIds={towerIds} towers={sim?.towers} onSelect={onSelect} selected={selected} />
        {sim && <CombatEffectsLayer sim={sim} view={view} />}
        {sim && <SimOverlay sim={sim} view={view} />}
      </svg>
      {selected && (
        <NodePopover node={selected} sim={sim} plan={plan} graphE={graphE}
          onClose={() => onSelect(null)} onRecruit={onRecruit} />
      )}
      {children}
    </div>
  );
}
