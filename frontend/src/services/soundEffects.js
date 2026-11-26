/**
 * Web Audio procedural sound effects service (Zero external sound files).
 * Synthesizes tactical game audio: clicks, shots, hits, coins, victory & defeat.
 */
class SoundEffectsService {
  constructor() {
    this.ctx = null;
    this.muted = false;
  }

  _init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume().catch(() => {});
  }

  toggleMute() {
    this.muted = !this.muted;
    return this.muted;
  }

  _tone(freq, type, dur, gainVal, delay = 0) {
    if (this.muted) return;
    this._init();
    if (!this.ctx) return;
    const t0 = this.ctx.currentTime + delay;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t0);
    gain.gain.setValueAtTime(gainVal, t0);
    gain.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t0);
    osc.stop(t0 + dur);
  }

  playClick() { this._tone(600, 'sine', 0.04, 0.08); }

  playRecruit() {
    [440, 554, 659].forEach((f, i) => this._tone(f, 'triangle', 0.08, 0.12, i * 0.05));
  }

  playShoot() {
    if (this.muted) return;
    this._init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(110, now + 0.08);
    gain.gain.setValueAtTime(0.14, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.08);
  }

  playExplosion() {
    if (this.muted) return;
    this._init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.25);
    gain.gain.setValueAtTime(0.28, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.25);
  }

  playCoin() {
    [987, 1318].forEach((f, i) => this._tone(f, 'sine', 0.12, 0.12, i * 0.07));
  }

  playVictory() {
    [523, 659, 784, 1046].forEach((f, i) => this._tone(f, 'triangle', 0.25, 0.18, i * 0.1));
  }

  playDefeat() {
    [392, 349, 311, 261].forEach((f, i) => this._tone(f, 'sawtooth', 0.25, 0.18, i * 0.12));
  }
}

export const sound = new SoundEffectsService();
