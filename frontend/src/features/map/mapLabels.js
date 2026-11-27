/** Turns the projected world into label requests (ids, tower places, bridges, soldiers) plus marker boxes. */
import { byId } from './mapGeometry';
import { around, along } from './labelLayout';

export const SOLDIER_COLOR = { INFANTRY: '#38bdf8', SNIPER: '#22c55e', GUNNER: '#f59e0b' };
export const onTheMove = (s) => s.status === 'MOVING' || s.status === 'FLYING';

export function buildLabels({ world, view, layers, towerIds }) {
  const { graphE, graphM, sim } = world;
  const { u, font } = view;
  const requests = [];
  const blocked = [];
  const height = font + 5;
  const widthOf = (text) => text.length * font * 0.61 + 9;
  const marker = ([x, y], size) => blocked.push({ x, y, w: size, h: size });
  const add = (id, priority, w, h, spots, extra) => requests.push({ id, priority, w, h, spots, ...extra });

  const name = (v, text, priority, first, extra) => add(`v-${v.id}`, priority, widthOf(text), height,
    around(v.coords[0], v.coords[1], u * 2.2, widthOf(text), height, first), { kind: 'name', text, ...extra });

  if (layers.ge) {
    graphE.vertices.forEach((v) => {
      marker(v.coords, u * 3.6);
      name(v, v.id, v.type === 'BASE' ? 2 : 3, 'below', {});
      if (!towerIds.includes(v.id)) return;
      const tower = sim?.towers.find((t) => t.vertex_id === v.id);
      add(`slots-${v.id}`, 0, u * 6.4, u * 2.4, around(v.coords[0], v.coords[1], u * 2.6, u * 6.4, u * 2.4, 'above'),
        { kind: 'slots', used: tower?.occupants ?? 0, reserved: tower?.reserved ?? 0 });
    });
  }
  if (layers.gm) {
    graphM.vertices.forEach((v) => {
      marker(v.coords, u * 3);
      const mark = v.is_entry ? '▶ ' : v.is_exit ? '⚑ ' : '';
      const color = v.is_entry ? '#16a34a' : v.is_exit ? '#dc2626' : '#ea580c';
      name(v, mark + v.id, mark ? 2 : 3, 'above', { color });
    });
    const verts = byId(graphM.vertices);
    graphM.corridors.forEach((c) => add(`c-${c.id}`, 6, widthOf(c.id), height - 2,
      along(verts[c.u].coords, verts[c.v].coords, height), { kind: 'tag', text: c.id, optional: true }));
  }
  if (layers.ge && sim) {
    const verts = byId(graphE.vertices);
    const live = byId(sim.bridges);
    graphE.edges.filter((e) => live[e.id]).forEach((e) => {
      const br = live[e.id];
      const hurt = br.destroyed || br.hp < br.max_hp;
      const text = br.destroyed ? (br.waiting_crew ? '✕ sin cuadrilla' : `✕ ${br.repair_left}s`) : `${br.hp}/${br.max_hp}`;
      add(`b-${e.id}`, hurt ? 1 : 5, widthOf(text), height, along(verts[e.u].coords, verts[e.v].coords, height),
        { kind: 'tag', text, tone: br.destroyed ? 'down' : hurt ? 'hurt' : 'bridge', optional: !hurt });
    });
  }
  if (sim) addSquads(sim, view, add, widthOf);
  if (sim?.convoy.enemies.some((e) => e.alive)) {
    const [x, y] = sim.convoy.xy;
    blocked.push({ x, y: y - u, w: u * 8, h: u * 7 });
  }
  return { requests, blocked };
}

/** Soldiers standing at the same vertex share one label: up to three dots, otherwise "×N" per type. */
function addSquads(sim, view, add, widthOf) {
  const { u, font } = view;
  const squads = {};
  sim.soldiers.filter((s) => !onTheMove(s)).forEach((s) => {
    (squads[s.vertex] ??= []).push(s);
  });
  Object.entries(squads).forEach(([vertex, list]) => {
    const compact = list.length <= 3;
    const counts = {};
    list.forEach((s) => { counts[s.type] = (counts[s.type] ?? 0) + 1; });
    const parts = compact
      ? list.map((s) => ({ color: SOLDIER_COLOR[s.type], faded: s.status === 'WAITING' }))
      : Object.entries(counts).map(([type, n]) => ({ color: SOLDIER_COLOR[type], text: `×${n}` }));
    const w = compact ? parts.length * u * 2.4 + 6 : parts.reduce((sum, p) => sum + u * 2.4 + widthOf(p.text) - 6, 6);
    const [x, y] = list[0].xy;
    add(`s-${vertex}`, 1, w, font + 6, around(x, y, u * 2.4, w, font + 6, 'below'), { kind: 'squad', parts, compact });
  });
}
