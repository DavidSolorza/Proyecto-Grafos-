import { useCallback, useEffect, useRef, useState } from 'react';
import * as api from '../api/client';

const FINISHED = ['VICTORY_ELIMINATION', 'VICTORY_RESISTANCE', 'DEFEAT'];
const FRAME_MS = 250; // real time between ticks; each tick advances 0.25s * speed

/** Holds the simulation snapshot and every action the user can trigger on it. */
export default function useSimulation() {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const busy = useRef(false);

  // Runs an API call and stores the new snapshot (or the error message)
  const run = useCallback(async (call, ...args) => {
    try {
      const res = await call(...args);
      setState(res.state);
      setError(null);
      return res.state;
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, []);

  useEffect(() => {
    api.fetchState().then((r) => setState(r.state)).catch(() => {}); // no match yet is fine
  }, []);

  useEffect(() => {
    if (!running) return undefined;
    const id = setInterval(async () => {
      if (busy.current) return; // do not queue ticks if the server is slow
      busy.current = true;
      const next = await run(api.tickSimulation, 0.25 * speed);
      busy.current = false;
      if (!next || FINISHED.includes(next.status)) setRunning(false);
    }, FRAME_MS);
    return () => clearInterval(id);
  }, [running, speed, run]);

  // Re-read the match (used when another client, like the Pygame app, changed it)
  const refresh = useCallback(async () => {
    try {
      const r = await api.fetchState();
      setState(r.state);
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
