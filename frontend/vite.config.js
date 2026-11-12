import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Defaults match the README. Override them when a port is busy:
//   VITE_PORT=5180 VITE_BACKEND_URL=http://127.0.0.1:5055 npm run dev
const backend = process.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:5000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.VITE_PORT ?? 5173),
    proxy: {
      '/api': {
        target: backend,
        changeOrigin: true,
      },
    },
  },
});
