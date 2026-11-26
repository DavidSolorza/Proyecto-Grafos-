import React, { useState } from 'react';
import { DollarSign, Clock, Volume2, VolumeX, Shield, Crosshair, Radar } from 'lucide-react';
import { sound } from '../../services/soundEffects';

/** Compact, translucent tactical HUD bar pinned cleanly to the top without covering nodes. */
export default function MapHud({ sim, plan, layers, onToggleLayer }) {
  const [muted, setMuted] = useState(sound.muted);

  const toggleSound = () => {
    const isMuted = sound.toggleMute();
    setMuted(isMuted);
    if (!isMuted) sound.playClick();
  };

  const alive = sim?.convoy ? sim.convoy.enemies.filter((e) => e.alive).length : 0;
  const total = sim?.convoy ? sim.convoy.enemies.length : 0;

  return (
    <div className="map-hud-bar" role="toolbar" aria-label="Controles tácticos del mapa">
      <div className="hud-group">
        {sim?.budget && (
          <div className="hud-tag cash">
            <DollarSign size={12} aria-hidden />
            <span className="mono">${sim.budget.available.toFixed(0)}</span>
          </div>
        )}
        {sim && (
          <div className="hud-tag time">
            <Clock size={12} aria-hidden />
            <span className="mono">{sim.clock.toFixed(1)}s</span>
          </div>
        )}
        {sim && total > 0 && (
          <div className={`hud-tag ${alive === 0 ? 'win' : 'enemy'}`}>
            <Shield size={12} aria-hidden />
            <span>{alive}/{total}</span>
          </div>
        )}
      </div>

      <div className="hud-group">
        <button
          type="button"
          className={`hud-btn-mini ${layers.radii ? 'on' : ''}`}
          onClick={() => onToggleLayer('radii')}
          title="Alternar radios de vigilancia Rv"
        >
          <Radar size={12} aria-hidden />
          <span>Rv</span>
        </button>
        <button
          type="button"
          className={`hud-btn-mini ${layers.tree ? 'on' : ''}`}
          onClick={() => onToggleLayer('tree')}
          title="Alternar árbol MST TE"
        >
          <Crosshair size={12} aria-hidden />
          <span>MST</span>
        </button>
        <button
          type="button"
          className="hud-btn-mini"
          onClick={toggleSound}
          title={muted ? 'Activar sonido' : 'Silenciar sonido'}
        >
          {muted ? <VolumeX size={12} aria-hidden /> : <Volume2 size={12} aria-hidden />}
        </button>
      </div>
    </div>
  );
}
