import React, { useEffect, useState } from 'react';
import { eventBus, EVENTS } from '../services/eventBus';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const unsub = eventBus.on(EVENTS.TOAST, (toast) => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev.slice(-4), { ...toast, id }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 4000);
    });
    return unsub;
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="toast-viewport" role="region" aria-label="Notificaciones">
      {toasts.map((t) => (
        <div key={t.id} className={`toast-card ${t.type || 'info'}`}>
          {t.type === 'error' && <AlertCircle size={18} />}
          {t.type === 'success' && <CheckCircle2 size={18} />}
          {(!t.type || t.type === 'info') && <Info size={18} />}
          <span style={{ flex: 1, fontWeight: '500' }}>{t.message}</span>
          <button
            className="toast-close"
            onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
            aria-label="Cerrar notificación"
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
