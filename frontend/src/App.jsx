import React, { useState } from 'react';
import Header from './components/Header';
import NoScenario from './components/NoScenario';
import IntroView from './features/intro/IntroView';
import GraphsView from './features/graphs/GraphsView';
import PlanView from './features/plan/PlanView';
import SimView from './features/simulation/SimView';
import useScenario from './hooks/useScenario';
import useSimulation from './hooks/useSimulation';
import useSync from './hooks/useSync';

export default function App() {
  const [tab, setTab] = useState('intro');
  const world = useScenario();
  const sim = useSimulation();
  useSync(world.reload, sim);

  // A new scenario or plan invalidates the running match
  const reload = async () => {
    await world.reload();
    sim.clear();
  };

  const calculatePlan = async () => {
    const plan = await world.calculatePlan();
    if (plan) await sim.reset();
    return plan;
  };

  return (
    <div className="app">
      <Header active={tab} onChange={setTab} isConnected={world.health.status === 'healthy'} />
      <main>
        {tab === 'intro' && (
          <IntroView scenario={world.scenario} validation={world.validation} error={world.error}
            loading={world.loading} onReload={reload} onNavigate={setTab} />
        )}
        {tab !== 'intro' && !world.scenario && <NoScenario loading={world.loading} onNavigate={setTab} />}
        {tab === 'graphs' && world.scenario && <GraphsView scenario={world.scenario} />}
        {tab === 'plan' && world.scenario && (
          <PlanView scenario={world.scenario} plan={world.plan} onCalculate={calculatePlan}
            error={world.error} onNavigate={setTab} />
        )}
        {tab === 'sim' && world.scenario && (
          <SimView scenario={world.scenario} plan={world.plan} ctrl={sim} onNavigate={setTab} />
        )}
      </main>
    </div>
  );
}
