/**
 * REST client for the Flask backend. Every function returns parsed JSON
 * or throws an Error with a message that is safe to show to the user.
 * In development Vite proxies /api to http://127.0.0.1:5000 (see vite.config.js).
 */
const API = import.meta.env.VITE_API_URL ?? '/api';

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API}${path}`, options);
  } catch {
    throw new Error('No se pudo conectar con el backend. ¿Está corriendo en el puerto 5000?');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false) {
    throw new Error(data.error || `Error del servidor (${res.status})`);
  }
  return data;
}

const post = (path, body = {}) =>
  request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

export const fetchHealth = () =>
  request('/health').catch((e) => ({ status: 'disconnected', error: e.message }));

export const fetchCurrentScenario = () => request('/scenario/current');

export const uploadScenarioFile = (file) => {
  const form = new FormData();
  form.append('file', file);
  return request('/scenario/upload', { method: 'POST', body: form });
};

// Defense plan (MST + towers)
export const fetchPlan = () => request('/defense/plan');
export const createPlan = () => post('/defense/plan');

// Simulation
export const fetchState = () => request('/simulation/state');
export const resetSimulation = () => post('/simulation/reset');
export const tickSimulation = (dt) => post('/simulation/tick', { dt });

// Units and transport
export const recruitSoldiers = (type, count = 1) => post('/units/recruit', { type, count });
export const moveSoldiers = (soldier_ids, dest, mode) =>
  post('/transport/move', { soldier_ids, dest, mode });
export const flyHelicopter = (soldier_ids, dest) =>
  post('/transport/helicopter', { soldier_ids, dest });
export const queryPath = (src, dst, mode) =>
  request(`/transport/path?src=${src}&dst=${dst}&mode=${mode}`);
