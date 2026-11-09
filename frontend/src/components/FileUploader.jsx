import React, { useState } from 'react';
import { uploadScenarioFile } from '../api/client';

export default function FileUploader({ onScenarioUploaded }) {
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setMsg(null);
    try {
      const res = await uploadScenarioFile(file);
      setMsg({ type: 'success', text: res.message });
      if (onScenarioUploaded) onScenarioUploaded();
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.title}>Cargar Escenario (.JSON)</span>
        <span style={styles.badge}>Requisito §12</span>
      </div>

      <div style={styles.uploadRow}>
        <input
          type="file"
          accept=".json"
          id="scenario-file-input"
          style={styles.hiddenInput}
          onChange={handleFileChange}
          disabled={loading}
        />
        <label htmlFor="scenario-file-input" style={styles.uploadButton}>
          {loading ? 'Validando...' : 'Seleccionar Archivo JSON'}
        </label>
        <span style={styles.hint}>Prohibidas rutas fijas. Sube tu escenario aquí.</span>
      </div>

      {msg && (
        <div style={msg.type === 'success' ? styles.successBox : styles.errorBox}>
          {msg.text}
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '10px',
    padding: '14px 20px',
    marginBottom: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#0f172a',
  },
  badge: {
    fontSize: '11px',
    backgroundColor: '#eff6ff',
    color: '#2563eb',
    padding: '2px 8px',
    borderRadius: '12px',
    fontWeight: '500',
  },
  uploadRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flexWrap: 'wrap',
  },
  hiddenInput: {
    display: 'none',
  },
  uploadButton: {
    padding: '8px 16px',
    backgroundColor: '#2563eb',
    color: '#ffffff',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    border: 'none',
  },
  hint: {
    fontSize: '12px',
    color: '#64748b',
  },
  successBox: {
    fontSize: '12px',
    color: '#065f46',
    backgroundColor: '#ecfdf5',
    padding: '6px 12px',
    borderRadius: '6px',
    border: '1px solid #a7f3d0',
  },
  errorBox: {
    fontSize: '12px',
    color: '#991b1b',
    backgroundColor: '#fef2f2',
    padding: '6px 12px',
    borderRadius: '6px',
    border: '1px solid #fecaca',
  },
};

