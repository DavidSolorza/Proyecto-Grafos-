import React from 'react';
import { Shield, Crosshair, Flame, X, UserPlus, MapPin } from 'lucide-react';
import { typeLabel } from './NodeLayer';

export default function NodePopover({ node, onClose, onRecruit, budget }) {
  if (!node) return null;

  const isBase = node.type === 'BASE';
  const isCandidate = node.type === 'CANDIDATE';

  return (
    <div className="node-popover-card" role="dialog" aria-label="Información táctica">
      <div className="node-popover-head">
        <span className="mono" style={{ fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
          <MapPin size={13} aria-hidden />
          {node.id} · {node.network === 'GE' ? typeLabel(node.type) : 'Laberinto'}
        </span>
        <button type="button" className="toast-close" onClick={onClose} aria-label="Cerrar">
          <X size={13} />
        </button>
      </div>

      <div className="node-popover-body font-xs">
        <div className="row spread mono font-2xs" style={{ color: 'var(--ink-soft)' }}>
          <span>Coords: [{node.coords?.[0]}, {node.coords?.[1]}]</span>
          {node.z !== undefined && <span>Altitud z: {node.z}</span>}
        </div>

        {isBase && onRecruit && (
          <div className="node-popover-actions mt-s">
            <b className="font-2xs" style={{ color: 'var(--ochre)', display: 'block', marginBottom: '4px' }}>
              Reclutar en Base:
            </b>
            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn ghost small font-2xs"
                onClick={() => onRecruit('infantry', 1)}
                disabled={budget?.available < 100}
                title="Infantería ($100)"
              >
                <Shield size={11} aria-hidden /> Inf. ($100)
              </button>
              <button
                type="button"
                className="btn ghost small font-2xs"
                onClick={() => onRecruit('sniper', 1)}
                disabled={budget?.available < 300}
                title="Francotirador ($300)"
              >
                <Crosshair size={11} aria-hidden /> Sniper ($300)
              </button>
              <button
                type="button"
                className="btn ghost small font-2xs"
                onClick={() => onRecruit('gunner', 1)}
                disabled={budget?.available < 500}
                title="Artillero ($500)"
              >
                <Flame size={11} aria-hidden /> Art. ($500)
              </button>
            </div>
          </div>
        )}

        {isCandidate && (
          <div className="mt-s font-2xs note">
            Posición defensiva elevada. Las torres admiten hasta 3 soldados de cualquier especialidad.
          </div>
        )}
      </div>
    </div>
  );
}
