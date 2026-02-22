import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8788',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    build: {
      outDir: '../dist',
      emptyOutDir: true,
      sourcemap: env.VITE_APP_DEBUG === 'true',
      minify: 'terser',
      cssCodeSplit: true,
      cssMinify: true,
      target: 'es2015',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            antd: ['antd', '@ant-design/icons'],
            echarts: ['echarts'],
            charts: ['recharts'],
            form: ['formik', 'yup']
          },
          assetFileNames: 'assets/[name]-[hash].[ext]',
          chunkFileNames: 'chunks/[name]-[hash].js',
          entryFileNames: 'entry/[name]-[hash].js',
          compact: true
        },
        treeshake: {
          moduleSideEffects: false,
          propertyReadSideEffects: false
        }
      },
      terserOptions: {
        compress: {
          drop_console: env.VITE_APP_ENV === 'production',
          drop_debugger: env.VITE_APP_ENV === 'production'
        }
      }
    },
    base: './'
  }
})
