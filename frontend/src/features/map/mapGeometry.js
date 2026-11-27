/** Projects both graphs from world units to screen pixels, so every size on the map can be clamped in px. */

export const clamp = (low, value, high) => Math.min(high, Math.max(low, value));

const MIN_PLOT = 640; // narrower boxes scroll sideways instead of shrinking the labels

export function computeView(graphE, graphM, boxWidth, screenHeight) {
  const points = [...(graphE?.vertices ?? []), ...(graphM?.vertices ?? [])].map((v) => v.coords);
  const xs = points.length ? points.map((p) => p[0]) : [0, 100];
  const ys = points.length ? points.map((p) => p[1]) : [0, 60];
  const dx = Math.max(...xs) - Math.min(...xs) || 1;
  const dy = Math.max(...ys) - Math.min(...ys) || 1;

  const w = Math.max(MIN_PLOT, Math.floor(boxWidth));
  const mx = clamp(52, w * 0.07, 88);
  const my = clamp(52, w * 0.06, 70);
  const maxHeight = clamp(420, screenHeight - 250, 660);
  const h = Math.round(clamp(400, ((w - 2 * mx) * dy) / dx + 2 * my, maxHeight));
  const scale = Math.min((w - 2 * mx) / dx, (h - 2 * my) / dy);
  const left = (w - dx * scale) / 2 - Math.min(...xs) * scale;
  const top = (h - dy * scale) / 2 - Math.min(...ys) * scale;
  const to = ([x, y]) => [left + x * scale, top + y * scale];
  // u: base unit for markers and strokes; font: label size, both in screen pixels
  return { w, h, scale, to, u: clamp(4.7, w / 150, 5.8), font: clamp(10, w / 72, 12) };
}

/** Same data with every position (and radius) expressed in pixels of the view. */
export function projectWorld(graphE, graphM, plan, sim, view) {
  const { to, scale } = view;
  const moved = (list) => list.map((v) => ({ ...v, coords: to(v.coords) }));
  const vertices = byId(graphE.vertices);
  const at = (t) => to(t.xy ?? (t.x !== undefined ? [t.x, t.y] : vertices[t.vertex_id].coords));
  const tower = (t) => ({ ...t, xy: at(t), rv: t.rv * scale });
  const unit = (item) => ({ ...item, xy: to(item.xy) });
  return {
    graphE: { ...graphE, vertices: moved(graphE.vertices) },
    graphM: { ...graphM, vertices: moved(graphM.vertices) },
    towers: (sim ? sim.towers : plan?.towers ?? []).map(tower),
    sim: sim && {
      ...sim,
      soldiers: sim.soldiers.map(unit),
      flights: sim.flights.map(unit),
      convoy: unit(sim.convoy),
    },
  };
}

/** Index vertices by id so edges can find their endpoints in O(1). */
export const byId = (list = []) => Object.fromEntries(list.map((v) => [v.id, v]));

export const midpoint = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];

/** Danger heat: 0 -> calm sand, 1 -> hot terracotta. */
export function heatColor(ratio) {
  const t = Math.max(0, Math.min(1, ratio));
  const from = [216, 200, 166];
  const to = [224, 83, 50];
  return `rgb(${from.map((c, i) => Math.round(c + (to[i] - c) * t)).join(',')})`;
}
