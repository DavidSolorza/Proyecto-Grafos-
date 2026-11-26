import React, { useEffect, useState } from 'react';
import { eventBus, EVENTS } from '../services/eventBus';
import { Activity, X } from 'lucide-react';

export default function HttpLogDrawer() {
  const [logs, setLogs] = useState([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const unsub = eventBus.on(EVENTS.HTTP_LOG, (entry) => {
      setLogs((prev) => [{ ...entry, id: Date.now() + Math.random() }, ...prev.slice(0, 24)]);
    });
    return unsub;
  }, []);

  return (
    <div className="http-drawer-pill">
      {open && (
        <div className="http-drawer-box">
          <div className="http-drawer-head">
            <span>Diagnóstico HTTP (API REST)</span>
            <button className="http-clear-btn" onClick={() => setLogs([])}>Limpiar</button>
          </div>
          {logs.length === 0 ? (
            <p className="note fine">Sin actividad de red registrada.</p>
          ) : (
            logs.map((log) => {
              const ok = log.status >= 200 && log.status < 400;
              return (
                <div key={log.id} className="http-row">
                  <span className={`http-method ${log.method.toLowerCase()}`}>{log.method}</span>
                  <span className="mono fine" style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {log.path}
                  </span>
                  <span className={`http-status ${ok ? 'ok' : 'err'}`}>
                    {log.status || 'ERR'}
                  </span>
                  <span className="mono fine" style={{ color: 'var(--sand)' }}>{log.duration}ms</span>
                </div>
              );
            })
          )}
        </div>
      )}
      <button
        className="http-drawer-btn"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Diagnóstico de red"
      >
        <Activity size={14} color="#0284c7" />
        <span>HTTP ({logs.length})</span>
      </button>
    </div>
  );
}
