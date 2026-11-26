/**
 * REST client for the Flask backend with HTTP status diagnostics & EventBus logs.
 */
import { eventBus, EVENTS } from '../services/eventBus';

const API = import.meta.env.VITE_API_URL ?? '/api';

const HTTP_ERRORS = {
  400: 'Solicitud inválida',
  401: 'No autorizado',
  403: 'Acceso denegado',
  404: 'Recurso no encontrado',
  409: 'Conflicto en el estado del escenario/simulación',
  500: 'Error interno del servidor Flask',
};

async function request(path, options = {}) {
  const method = options.method || 'GET';
  const silent = Boolean(options.silent);
  const start = performance.now();
  let res;
  try {
    res = await fetch(`${API}${path}`, options);
  } catch (err) {
    const duration = Math.round(performance.now() - start);
    if (!silent) eventBus.emit(EVENTS.HTTP_LOG, { method, path, status: 0, error: err.message, duration });
    throw new Error('No se pudo conectar con el backend. ¿Está corriendo en el puerto 5000?');
  }

  const duration = Math.round(performance.now() - start);
  const data = await res.json().catch(() => ({}));
  if (!silent) eventBus.emit(EVENTS.HTTP_LOG, { method, path, status: res.status, success: res.ok, duration });

  if (!res.ok || data.success === false) {
    const desc = HTTP_ERRORS[res.status] || `Error HTTP ${res.status}`;
    const msg = data.error ? `${data.error}` : `${desc}`;
    if (!silent && res.status !== 409) {
      eventBus.emit(EVENTS.TOAST, { type: 'error', message: `[${res.status}] ${msg}` });
    }
    throw new Error(msg);
  }
  return data;
}

const post = (path, body = {}, options = {}) =>
  request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    ...options,
  });

export const fetchHealth = () =>
  request('/health', { silent: true }).catch((e) => ({ status: 'disconnected', error: e.message }));

export const fetchCurrentScenario = () => request('/scenario/current');
export const fetchStatus = () => request('/scenario/status', { silent: true });

export const uploadScenarioFile = (file) => {
  const form = new FormData();
  form.append('file', file);
  return request('/scenario/upload', { method: 'POST', body: form });
};

export const fetchPlan = () => request('/defense/plan', { silent: true });
export const createPlan = () => post('/defense/plan');

export const fetchState = (silent = false) => request('/simulation/state', { silent });
export const resetSimulation = () => post('/simulation/reset');
export const tickSimulation = (dt) => post('/simulation/tick', { dt });

export const recruitSoldiers = (type, count = 1) => post('/units/recruit', { type, count });
export const moveSoldiers = (soldier_ids, dest, mode) =>
  post('/transport/move', { soldier_ids, dest, mode });
export const flyHelicopter = (soldier_ids, dest) =>
  post('/transport/helicopter', { soldier_ids, dest });
export const queryPath = (src, dst, mode) =>
  request(`/transport/path?src=${src}&dst=${dst}&mode=${mode}`);
