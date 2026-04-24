import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/append': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/api/dashboard': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/dashboard/, '')
      }
    }
  }
})
