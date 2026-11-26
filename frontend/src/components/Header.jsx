import React from 'react';
import { Home, Share2, ShieldAlert, Play, Wifi, WifiOff } from 'lucide-react';

export const TABS = [
  { id: 'intro', n: '01', label: 'Inicio', icon: Home },
  { id: 'graphs', n: '02', label: 'Los grafos', icon: Share2 },
  { id: 'plan', n: '03', label: 'Plan de defensa', icon: ShieldAlert },
  { id: 'sim', n: '04', label: 'Simulación', icon: Play },
];

export default function Header({ active, onChange, isConnected }) {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <div className="brand-title">
            <span className="brand-mark" aria-hidden="true" />
            <h1>
              General P. Tardo
              <small>Defensa de Corredor · Universidad de Caldas</small>
            </h1>
          </div>
          <div className={`status-pill ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? <Wifi size={14} className="icon-pulse" /> : <WifiOff size={14} />}
            <span className="pill-text">{isConnected ? 'API Flask Online' : 'API Desconectada'}</span>
          </div>
        </div>
        <nav className="tabs" aria-label="Secciones">
          {TABS.map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                className={`tab ${active === t.id ? 'active' : ''}`}
                onClick={() => onChange(t.id)}
                aria-current={active === t.id ? 'page' : undefined}
              >
                <Icon size={15} style={{ marginRight: '6px' }} />
                <span>{t.n}</span>
                {t.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
