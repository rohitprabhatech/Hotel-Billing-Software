import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend run.py listens on 5003 (not 5000).
const API_ORIGIN = 'http://127.0.0.1:5003'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: API_ORIGIN,
        changeOrigin: true,
      },
    },
  },
})
