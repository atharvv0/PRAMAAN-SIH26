import path from 'node:path'
import { fileURLToPath } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

const rootDir = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, rootDir, '')
  const apiBaseUrl = (env.VITE_API_BASE_URL || '/api/v1').trim()
  const devApiTarget = (env.VITE_DEV_API_TARGET || 'http://127.0.0.1:8000').trim()

  const proxyPrefix = apiBaseUrl.startsWith('/')
    ? apiBaseUrl.split('/').filter(Boolean).slice(0, 2).reduce((value, part) => `${value}/${part}`, '') || '/api'
    : null

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(rootDir, 'src'),
      },
    },
    server: {
      port: 5173,
      strictPort: true,
      proxy:
        proxyPrefix
          ? {
              [proxyPrefix]: {
                target: devApiTarget,
                changeOrigin: false,
              },
            }
          : undefined,
    },
  }
})
