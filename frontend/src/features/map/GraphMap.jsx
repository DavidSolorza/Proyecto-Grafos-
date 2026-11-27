import React, { useRef, useState } from 'react';
import { byId, computeView, projectWorld } from './mapGeometry';
import useBoxWidth from './useBoxWidth';
import { CorridorLayer, EdgeLayer, RadiusLayer } from './MapLayers';
import { NodeLayer } from './NodeLayer';
import LabelLayer from './LabelLayer';
import SimOverlay from './SimOverlay';
import CombatEffectsLayer from './CombatEffectsLayer';
import MapHud from './MapHud';
import NodePopover from './NodePopover';
import '../../styles/map.css';

/** Responsive SVG battlefield drawn in screen pixels: corridors, walkways, units, labels and HUD. */
export default function GraphMap({
  graphE, graphM, plan, sim, layers: initialLayers = { ge: true, gm: true, tree: false, radii: false },
  selected, onSelect = () => {}, onRecruit, children, routeIds = [],
}) {
  const [toggled, setToggled] = useState({});
  const scroller = useRef(null);
  const boxWidth = useBoxWidth(scroller);
  if (!graphE || !graphM) return null;
  const layers = { ...initialLayers, ...toggled };
  const view = computeView(graphE, graphM, boxWidth, window.innerHeight);
  const world = projectWorld(graphE, graphM, plan, sim, view);
  const towerIds = world.towers.map((t) => t.vertex_id);

  const toggleLayer = (k) => setToggled((prev) => ({ ...prev, [k]: !layers[k] }));
  // Popovers and details must show the original coordinates, not the pixel ones
  const pick = (node) => {
    const source = node.network === 'GE' ? graphE : graphM;
    onSelect({ ...byId(source.vertices)[node.id], network: node.network });
  };

  return (
    <div className="stage tactical-stage">
      {sim && <MapHud sim={sim} layers={layers} onToggleLayer={toggleLayer} />}
      <div className="map-scroll" ref={scroller}>
        <svg className="map-svg" width={view.w} height={view.h} viewBox={`0 0 ${view.w} ${view.h}`} role="img"
          aria-label="Mapa de batalla táctico: red elevada GE y laberinto GM">
          <defs>
            <pattern id="tac-grid" width={view.u * 8} height={view.u * 8} patternUnits="userSpaceOnUse">
              <path d={`M ${view.u * 8} 0 L 0 0 0 ${view.u * 8}`} fill="none" stroke="rgba(148, 163, 184, 0.22)" strokeWidth={view.u * 0.15} />
            </pattern>
            <filter id="node-shadow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="1.5" stdDeviation="1" floodColor="#0f172a" floodOpacity="0.25" />
            </filter>
          </defs>
          <rect width={view.w} height={view.h} fill="url(#tac-grid)" />
          {layers.radii && world.towers.length > 0 && <RadiusLayer towers={world.towers} view={view} />}
          {layers.gm && (
            <CorridorLayer graphM={world.graphM} view={view} simCorridors={sim?.corridors} routeIds={routeIds}
              covered={plan?.covered_corridors} showCoverage={layers.tree && !sim} />
          )}
          {layers.ge && (
            <EdgeLayer graphE={world.graphE} view={view} bridges={sim?.bridges}
              treeIds={plan?.mst.edges.map((e) => e.id)} showTree={layers.tree} />
          )}
          <NodeLayer graphE={world.graphE} graphM={world.graphM} view={view} showE={layers.ge} showM={layers.gm}
            towerIds={towerIds} onSelect={pick} selected={selected} />
          {world.sim && <CombatEffectsLayer sim={world.sim} view={view} />}
          {world.sim && <SimOverlay sim={world.sim} view={view} />}
          <LabelLayer world={world} view={view} layers={layers} towerIds={towerIds} />
        </svg>
      </div>
      {boxWidth > 0 && boxWidth < view.w && <p className="map-hint">← Desliza el mapa para verlo completo →</p>}
      {selected && (
        <NodePopover node={selected} sim={sim} plan={plan} graphE={graphE}
          onClose={() => onSelect(null)} onRecruit={onRecruit} />
      )}
      {children}
    </div>
  );
}
