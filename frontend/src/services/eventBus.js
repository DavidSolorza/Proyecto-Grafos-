/**
 * Event Bus Service for decoupled, high-performance pub/sub messaging.
 * Prevents sluggishness and unnecessary full component tree re-renders.
 */
class EventBusService {
  constructor() {
    this.listeners = new Map();
    this.throttleTimers = new Map();
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    const set = this.listeners.get(event);
    if (set) {
      set.delete(callback);
      if (set.size === 0) this.listeners.delete(event);
    }
  }

  emit(event, payload) {
    const set = this.listeners.get(event);
    if (set) {
      set.forEach((cb) => {
        try {
          cb(payload);
        } catch (err) {
          console.error(`[EventBus] Error in listener for "${event}":`, err);
        }
      });
    }
  }

  emitThrottled(event, payload, waitMs = 50) {
    if (this.throttleTimers.has(event)) return;
    this.emit(event, payload);
    const timer = setTimeout(() => {
      this.throttleTimers.delete(event);
    }, waitMs);
    this.throttleTimers.set(event, timer);
  }

  clear() {
    this.throttleTimers.forEach(clearTimeout);
    this.throttleTimers.clear();
    this.listeners.clear();
  }
}

export const eventBus = new EventBusService();

export const EVENTS = {
  SIM_TICK: 'sim:tick',
  COMBAT: 'sim:combat',
  BRIDGE: 'sim:bridge',
  HTTP_LOG: 'http:log',
  TOAST: 'ui:toast',
  SCENARIO_CHANGED: 'scenario:changed',
};
