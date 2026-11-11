/** Helpers to fit both graphs inside one responsive SVG viewBox. */

export function computeView(graphE, graphM, extra = 0) {
  const points = [...(graphE?.vertices ?? []), ...(graphM?.vertices ?? [])].map((v) => v.coords);
  if (points.length === 0) return { minX: 0, minY: 0, w: 100, h: 60, u: 1 };
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const pad = Math.max(...xs, ...ys) * 0.12 + 6 + extra;
  const minX = Math.min(...xs) - pad;
  const minY = Math.min(...ys) - pad;
  const w = Math.max(...xs) - Math.min(...xs) + pad * 2;
  const h = Math.max(...ys) - Math.min(...ys) + pad * 2;
  return { minX, minY, w, h, u: Math.max(w, h) / 100 }; // u = one "pixel-ish" unit
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
