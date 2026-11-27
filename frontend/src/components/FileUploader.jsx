import React, { useState } from 'react';
import { uploadScenarioFile } from '../api/client';
import { UploadCloud, FileCheck, AlertCircle } from 'lucide-react';

/** Lets the user choose or drop any scenario .json: there are no fixed input paths. */
export default function FileUploader({ onUploaded }) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const [dragging, setDragging] = useState(false);

  const processFile = async (file) => {
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
    }
  };

  return (
    <div
      className={`card ${dragging ? 'drag-over' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); processFile(e.dataTransfer.files?.[0]); }}
      style={{
        border: dragging ? '2px dashed #2563eb' : '1px solid #e2e8f0',
        backgroundColor: dragging ? '#eff6ff' : '#ffffff',
        transition: 'all 0.2s ease',
      }}
    >
      <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <UploadCloud size={18} color="#2563eb" />
        <h3>Cargar Escenario</h3>
        <span className="badge" style={{ marginLeft: 'auto' }}>.json</span>
      </div>
      <p className="note mb-m font-sm">
        Arrastra tu archivo JSON o elígelo. El backend valida ambos grafos, base e invariantes antes de activarlo.
      </p>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '14px' }}>
        <label className="btn small" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          {busy ? <FileCheck size={14} className="spin" /> : <UploadCloud size={14} />}
          {busy ? 'Validando…' : 'Subir archivo JSON'}
          <input type="file" accept=".json,application/json" onChange={(e) => processFile(e.target.files?.[0])} disabled={busy} hidden />
        </label>
      </div>

      {msg && (
        <div className={`alert ${msg.type} mt-m`} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {msg.type === 'error' ? <AlertCircle size={15} /> : <FileCheck size={15} />}
          <span>{msg.text}</span>
        </div>
      )}
    </div>
  );
}
