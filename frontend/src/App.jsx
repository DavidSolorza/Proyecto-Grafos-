import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import FileUploader from './components/FileUploader';
import ScenarioOverview from './components/ScenarioOverview';
import MapView from './features/map/MapView';
import { fetchHealth, fetchCurrentScenario } from './api/client';

export default function App() {
  const [health, setHealth] = useState({ status: 'connecting' });
  const [scenario, setScenario] = useState(null);
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadScenario = useCallback(async () => {
    try {
      const res = await fetchCurrentScenario();
      if (res.success) {
        setScenario(res.data);
        setValidation(res.validation);
      }
    } catch (err) {
      setError(err.message || 'Error cargando datos del escenario');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth().then(setHealth);
    loadScenario();
  }, [loadScenario]);

  const isConnected = health.status === 'healthy';

  return (
    <div style={styles.appContainer}>
      <Header isConnected={isConnected} serviceName={health.service} />

      <main style={styles.main}>
        <FileUploader onScenarioUploaded={loadScenario} />

        {validation && (
          <div style={styles.validationBar}>
            <strong>Invariantes del Grafo: </strong>
            <span>Base presente: {validation.has_base ? '✓' : '✗'} | </span>
            <span>Componente conexa base: {validation.base_connected ? '✓' : '✗'} | </span>
            <span>Camino Entrada-Salida: {validation.labyrinth_path_exists ? '✓' : '✗'}</span>
          </div>
        )}

        {loading && <div style={styles.notice}>Cargando escenario...</div>}
        {error && <div style={styles.error}>{error}</div>}

        {scenario && (
          <>
            <ScenarioOverview metadata={scenario.metadata} convoy={scenario.convoy} />
            <MapView graphE={scenario.graph_e} graphM={scenario.graph_m} />
          </>
        )}
      </main>
    </div>
  );
}

const styles = {
  appContainer: { minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' },
  main: { flex: 1, maxWidth: '1100px', width: '100%', margin: '0 auto', padding: '20px' },
  validationBar: { marginBottom: '16px', padding: '10px 14px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', fontSize: '12px', color: '#166534' },
  notice: { padding: '14px', backgroundColor: '#eff6ff', borderRadius: '8px', color: '#1e40af', fontSize: '13px' },
  error: { padding: '14px', backgroundColor: '#fff1f2', borderRadius: '8px', color: '#9f1239', fontSize: '13px' },
};
