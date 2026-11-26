import React, { useState } from 'react';
import { uploadScenarioFile } from '../api/client';
import { UploadCloud, FileCheck, AlertCircle, Sparkles } from 'lucide-react';

const SAMPLES = [
  { id: 'escenario_general_p_tardo.json', label: 'General P. Tardo (Base)' },
  { id: 'escenario_asedio_final.json', label: 'El Asedio Final' },
  { id: 'escenario_complejo.json', label: 'Complejo (11 Nodos)' },
  { id: 'escenario_puentes.json', label: 'Puentes Frágiles' },
  { id: 'escenario_cuadrilla.json', label: 'Cuadrilla de Reparación' },
];

/** Lets the user choose, drop or 1-click load any scenario .json. */
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

  const loadSample = async (filename) => {
    setBusy(true);
    setMsg(null);
    try {
      const res = await fetch(`/scenarios/${filename}`);
      if (!res.ok) throw new Error(`No se pudo cargar /scenarios/${filename}`);
      const blob = await res.blob();
      const file = new File([blob], filename, { type: 'application/json' });
      await processFile(file);
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
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

      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
          <Sparkles size={14} color="#d97706" />
          <b className="font-xs" style={{ color: '#475569' }}>Escenarios precargados de prueba (1 clic):</b>
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {SAMPLES.map((s) => (
            <button
              key={s.id}
              type="button"
              className="btn ghost small font-2xs"
              onClick={() => loadSample(s.id)}
              disabled={busy}
              style={{ padding: '4px 10px' }}
            >
              {s.label}
            </button>
          ))}
        </div>
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
