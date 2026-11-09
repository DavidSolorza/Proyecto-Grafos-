import React from 'react';

export default function Header({ isConnected, serviceName }) {
  return (
    <header style={styles.header}>
      <div>
        <h1 style={styles.title}>Defensa del Corredor Estratégico</h1>
        <p style={styles.subtitle}>
          Simulación: Derrota del Dictador General P. Tardo
        </p>
      </div>

      <div style={styles.statusBadge}>
        <span
          style={{
            ...styles.dot,
            backgroundColor: isConnected ? '#10b981' : '#f43f5e',
          }}
        />
        <span style={styles.statusText}>
          {isConnected ? `Backend Conectado (${serviceName})` : 'Backend Desconectado'}
        </span>
      </div>
    </header>
  );
}

const styles = {
  header: {
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e2e8f0',
    padding: '16px 28px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  },
  title: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#0f172a',
  },
  subtitle: {
    fontSize: '13px',
    color: '#64748b',
    marginTop: '2px',
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#f1f5f9',
    padding: '6px 12px',
    borderRadius: '20px',
    border: '1px solid #cbd5e1',
  },
  dot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
  },
  statusText: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#334155',
  },
};

