import React from 'react';

/** Collapsible "how does this work?" box. Useful when presenting each algorithm. */
export default function Explainer({ title, children, open = false }) {
  return (
    <details className="explainer" open={open}>
      <summary>{title}</summary>
      <div>{children}</div>
    </details>
  );
}
