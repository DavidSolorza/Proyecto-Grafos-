/** Places map labels so they do not cover each other or the markers. Boxes are {x, y, w, h}, x/y = centre. */
import { clamp } from './mapGeometry';

/** Candidate centres around a point, nearest ring first. */
export function around(x, y, gap, w, h, first = 'below') {
  const spots = [];
  for (const extra of [0, 12, 24, 38]) {
    const up = y - gap - extra - h / 2;
    const down = y + gap + extra + h / 2;
    const side = gap + extra + w / 2;
    const vertical = first === 'below' ? [[x, down], [x, up]] : [[x, up], [x, down]];
    spots.push(...vertical, [x + side, y], [x - side, y],
      [x + side * 0.8, down], [x - side * 0.8, down], [x + side * 0.8, up], [x - side * 0.8, up]);
  }
  return spots;
}

/** Candidate centres on and beside a segment. */
export function along(a, b, h) {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const len = Math.hypot(dx, dy) || 1;
  const spots = [];
  for (const side of [0, 1, -1, 2, -2]) {
    for (const t of [0.5, 0.37, 0.63, 0.25, 0.75]) {
      spots.push([a[0] + dx * t - (dy / len) * side * h, a[1] + dy * t + (dx / len) * side * h]);
    }
  }
  return spots;
}

const overlap = (a, b) => Math.max(0, (a.w + b.w) / 2 + 1 - Math.abs(a.x - b.x))
  * Math.max(0, (a.h + b.h) / 2 + 1 - Math.abs(a.y - b.y));

/** Most important labels first; optional ones are left out when no free spot exists. */
export function placeLabels(requests, blocked, bounds) {
  const taken = [...blocked];
  const placed = [];
  for (const req of [...requests].sort((a, b) => a.priority - b.priority)) {
    let best = null;
    for (const [sx, sy] of req.spots) {
      const box = {
        w: req.w, h: req.h,
        x: clamp(req.w / 2 + 2, sx, bounds.w - req.w / 2 - 2),
        y: clamp(req.h / 2 + 2, sy, bounds.h - req.h / 2 - 2),
      };
      const cost = taken.reduce((sum, other) => sum + overlap(box, other), 0);
      if (!best || cost < best.cost) best = { box, cost };
      if (cost === 0) break;
    }
    if (best && (best.cost === 0 || !req.optional)) {
      taken.push(best.box);
      placed.push({ ...req, ...best.box });
    }
  }
  return placed;
}
