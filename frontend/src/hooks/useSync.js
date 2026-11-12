import { useEffect, useRef } from 'react';
import { fetchStatus } from '../api/client';

const POLL_MS = 1500;

/**
 * The Flask session is shared with the Pygame client. Every 1.5 s this asks for a tiny
 * fingerprint of the session and, only when it changed, re-reads scenario, plan and match.
 * While this app is running its own match it skips the check: it is the one changing the session.
 */
export default function useSync(reloadWorld, sim) {
  const last = useRef(null);
  const { running, refresh } = sim;

  useEffect(() => {
    let alive = true;
    const id = setInterval(async () => {
      if (running) return;
      try {
        const status = await fetchStatus();
        const fingerprint = JSON.stringify([status.revision, status.match]);
        if (!alive || fingerprint === last.current) return;
        last.current = fingerprint;
        // The first fingerprint also reloads: a client may have changed the session after this page first loaded
        await reloadWorld(true);
        await refresh();
      } catch {
        last.current = null; // backend unreachable: compare from scratch when it is back
      }
    }, POLL_MS);
    return () => { alive = false; clearInterval(id); };
  }, [running, refresh, reloadWorld]);
}
