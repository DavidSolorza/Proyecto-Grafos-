import React from 'react';

/** Table per iteration of the greedy algorithm: shows C(p), D_T and S(p) of every candidate. */
export default function PlanSteps({ steps }) {
  if (!steps.length) return <p>Ningún candidato aporta cobertura nueva.</p>;
  return (
    <div className="stack">
      {steps.map((step) => (
        <div key={step.iteration}>
          <h3 style={{ marginBottom: 6 }}>
            Iteración {step.iteration} → <span style={{ color: 'var(--ochre)' }}>{step.chosen}</span>
          </h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Candidata</th><th>C(p)</th><th>D_T(B,p)</th><th>S(p)</th></tr>
              </thead>
              <tbody>
                {step.scores.map((s) => (
                  <tr key={s.vertex_id} className={s.vertex_id === step.chosen ? 'picked' : ''}>
                    <td>{s.vertex_id}</td>
                    <td className="num">{s.gain.toFixed(1)}</td>
                    <td className="num">{s.dt.toFixed(1)}s</td>
                    <td className="num">{s.score.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: '0.8rem', marginTop: 4 }}>
            Corredores que pasan a estar vigilados: {step.new_corridors.join(', ') || 'ninguno'}.
          </p>
        </div>
      ))}
    </div>
  );
}
