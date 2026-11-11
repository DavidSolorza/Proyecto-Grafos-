import React, { useState } from 'react';
import { uploadScenarioFile } from '../api/client';

/** Lets the user choose any scenario .json (no fixed paths, requirement §12). */
export default function FileUploader({ onUploaded }) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMsg(null);
    try {
      const res = await uploadScenarioFile(file);
      setMsg({ type: 'ok', text: res.message });
      onUploaded();
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
    } finally {
      setBusy(false);
      e.target.value = ''; // lets the user pick the same file again
    }
  };

  return (
    <div className="card">
      <div className="card-title">
        <h3>Cargar escenario</h3>
        <span className="badge">.json</span>
      </div>
      <p style={{ marginBottom: 12, fontSize: '0.88rem' }}>
        Elige un archivo con los dos grafos, el convoy y los parámetros. El backend lo valida antes de usarlo.
      </p>
      <label className="btn ghost small" style={{ display: 'inline-block' }}>
        {busy ? 'Validando…' : 'Seleccionar archivo'}
        <input type="file" accept=".json,application/json" onChange={handleFile} disabled={busy} hidden />
      </label>
      {msg && <div className={`alert ${msg.type}`} style={{ marginTop: 12 }}>{msg.text}</div>}
    </div>
  );
}
