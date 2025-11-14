import { defineConfig } from 'vite'
import elm from 'vite-plugin-elm'

export default defineConfig({
  plugins: [elm()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist'
  }
})
