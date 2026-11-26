import { useCallback, useEffect, useRef, useState } from 'react';
import * as api from '../api/client';
import { eventBus, EVENTS } from '../services/eventBus';

const FINISHED = ['VICTORY_ELIMINATION', 'VICTORY_RESISTANCE', 'DEFEAT'];
const FRAME_MS = 250;

/** Holds simulation state and coordinates high-performance updates via EventBus. */
export default function useSimulation() {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const busy = useRef(false);

  const run = useCallback(async (call, ...args) => {
    try {
      const res = await call(...args);
      setState(res.state);
      setError(null);
      eventBus.emit(EVENTS.SIM_TICK, res.state);
      return res.state;
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, []);

  useEffect(() => {
    api.fetchState().then((r) => {
      setState(r.state);
      eventBus.emit(EVENTS.SIM_TICK, r.state);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!running) return undefined;
    const id = setInterval(async () => {
      if (busy.current) return;
      busy.current = true;
      const next = await run(api.tickSimulation, 0.25 * speed);
      busy.current = false;
      if (!next || FINISHED.includes(next.status)) setRunning(false);
    }, FRAME_MS);
    return () => clearInterval(id);
  }, [running, speed, run]);

  const refresh = useCallback(async () => {
    try {
      const r = await api.fetchState();
      setState(r.state);
      eventBus.emit(EVENTS.SIM_TICK, r.state);
      if (FINISHED.includes(r.state.status)) setRunning(false);
    } catch {
      setState(null);
      setRunning(false);
    }
  }, []);

  return {
    refresh, state, error, running, speed, setSpeed, clearError: () => setError(null),
    finished: state ? FINISHED.includes(state.status) : false,
    togglePlay: () => setRunning((r) => !r),
    clear: () => { setRunning(false); setState(null); setError(null); },
    reset: async () => { setRunning(false); return run(api.resetSimulation); },
    step: () => run(api.tickSimulation, 1),
    recruit: (type, count) => run(api.recruitSoldiers, type, count),
    move: (ids, dest, mode) => run(api.moveSoldiers, ids, dest, mode),
    fly: (ids, dest) => run(api.flyHelicopter, ids, dest),
  };
}
