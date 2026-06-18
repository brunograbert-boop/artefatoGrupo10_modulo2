import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base: './' permite abrir o build do file:// (entrega ao professor sem servidor)
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    assetsInlineLimit: 1024 * 1024,
  },
})
