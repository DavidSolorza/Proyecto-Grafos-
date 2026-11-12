import React from 'react';
import { computeView } from './mapGeometry';
import { CorridorLayer, EdgeLayer, RadiusLayer } from './MapLayers';
import { NodeLayer } from './NodeLayer';
import SimOverlay from './SimOverlay';
import '../../styles/map.css';

/**
 * Responsive SVG that draws both graphs at once.
 * Optional props add the defense plan (tree, towers, radii) and the live simulation.
 */
export default function GraphMap({
  graphE, graphM, plan, sim, layers = { ge: true, gm: true, tree: false, radii: false },
  selected, onSelect = () => {}, children, routeIds = [],
}) {
  if (!graphE || !graphM) return null;
  const view = computeView(graphE, graphM);
  const towerIds = sim ? sim.towers.map((t) => t.vertex_id) : (plan?.towers ?? []).map((t) => t.vertex_id);
  const towerPoints = sim
    ? sim.towers
    : (plan?.towers ?? []).map((t) => ({ ...t, xy: graphE.vertices.find((v) => v.id === t.vertex_id)?.coords }));

  return (
    <div className="stage">
      <svg viewBox={`${view.minX} ${view.minY} ${view.w} ${view.h}`} role="img"
        aria-label="Mapa con la red elevada GE y el laberinto GM" preserveAspectRatio="xMidYMid meet">
        <defs>
          <pattern id="grid" width={view.u * 10} height={view.u * 10} patternUnits="userSpaceOnUse">
            <path d={`M ${view.u * 10} 0 L 0 0 0 ${view.u * 10}`} fill="none" stroke="rgba(240,231,214,0.06)" strokeWidth={view.u * 0.2} />
          </pattern>
        </defs>
        <rect x={view.minX} y={view.minY} width={view.w} height={view.h} fill="url(#grid)" />
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
        {sim && <SimOverlay sim={sim} view={view} />}
      </svg>
      {children}
    </div>
  );
}
