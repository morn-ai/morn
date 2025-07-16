import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  root: 'src',
  build: {
    outDir: '../dist',
  },
  server: {
    proxy: {
      "/auth": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth/, "/"),
      },
    },
  },
})
