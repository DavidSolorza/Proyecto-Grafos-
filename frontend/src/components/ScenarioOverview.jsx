import React from 'react';

export default function ScenarioOverview({ metadata, convoy }) {
  if (!metadata) return null;

  const items = [
    { label: 'Presupuesto Inicial', value: `$${metadata.initial_budget}` },
    { label: 'Tiempo Ref. D0', value: `${metadata.d0}s` },
    { label: 'Coef. Daño (α)', value: metadata.alpha },
    { label: 'Coef. Altura (β)', value: metadata.beta },
    { label: 'Máx. Torres (K)', value: metadata.max_towers_k },
    { label: 'Reparación Puente', value: `${metadata.bridge_repair_time}s` },
  ];

  return (
    <section style={styles.card}>
      <h2 style={styles.heading}>Parámetros del Escenario</h2>
      <div style={styles.grid}>
        {items.map((it) => (
          <div key={it.label} style={styles.item}>
            <span style={styles.label}>{it.label}</span>
            <span style={styles.val}>{it.value}</span>
          </div>
        ))}
      </div>

      {convoy && (
        <div style={styles.convoyBox}>
          <strong style={styles.convoyTitle}>Convoy Enemigo: </strong>
          <span style={styles.convoyText}>
            Tanques: {convoy.tanks} | Camiones: {convoy.trucks} | Soldados Robot: {convoy.robot_soldiers}
          </span>
        </div>
      )}
    </section>
  );
}

const styles = {
  card: {
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '10px',
    padding: '18px 22px',
    marginBottom: '20px',
    boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
  },
  heading: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '14px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: '12px',
  },
  item: {
    backgroundColor: '#f8fafc',
    padding: '10px 12px',
    borderRadius: '6px',
    border: '1px solid #e2e8f0',
  },
  label: {
    display: 'block',
    fontSize: '11px',
    color: '#64748b',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  val: {
    display: 'block',
    fontSize: '16px',
    fontWeight: '600',
    color: '#0f172a',
    marginTop: '3px',
  },
  convoyBox: {
    marginTop: '14px',
    padding: '10px 14px',
    backgroundColor: '#fffbeb',
    border: '1px solid #fef3c7',
    borderRadius: '6px',
    fontSize: '13px',
  },
  convoyTitle: {
    color: '#b45309',
  },
  convoyText: {
    color: '#92400e',
  },
};

