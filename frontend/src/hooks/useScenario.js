import { useCallback, useEffect, useState } from 'react';
import { createPlan, fetchCurrentScenario, fetchHealth, fetchPlan } from '../api/client';

/** Loads the active scenario, its validation, the backend status and the defense plan. */
export default function useScenario() {
  const [health, setHealth] = useState({ status: 'connecting' });
  const [scenario, setScenario] = useState(null);
  const [validation, setValidation] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // `silent` re-reads the backend without flashing the loading state or clearing the visible error
  const load = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true);
      setError(null);
    }
    try {
      const [res, planRes] = await Promise.all([fetchCurrentScenario(), fetchPlan()]);
      setScenario(res.data);
      setValidation(res.validation);
      setPlan(planRes.plan);
    } catch (err) {
      if (!silent) setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth().then(setHealth);
    load();
  }, [load]);

  const calculatePlan = useCallback(async () => {
    setError(null);
    try {
      const res = await createPlan();
      setPlan(res.plan);
      return res.plan;
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, []);

  return { health, scenario, validation, plan, loading, error, reload: load, calculatePlan };
}
