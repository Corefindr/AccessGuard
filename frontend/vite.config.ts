import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

const FRONTEND_PORT = 43123
const DEFAULT_API_ORIGIN = 'http://127.0.0.1:8472'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiOrigin = env.VITE_API_BASE_URL || DEFAULT_API_ORIGIN

  return {
    plugins: [react(), tailwindcss()],
    server: {
      host: '127.0.0.1',
      port: FRONTEND_PORT,
      strictPort: true,
      proxy: {
        '/api': {
          target: apiOrigin,
          changeOrigin: true,
        },
      },
    },
    preview: {
      host: '127.0.0.1',
      port: FRONTEND_PORT,
    },
  }
})
