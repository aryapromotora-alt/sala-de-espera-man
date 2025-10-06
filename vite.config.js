import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// As importações do tailwindcss e autoprefixer foram removidas daqui.

export default defineConfig({
  plugins: [
    react({
      jsxRuntime: 'automatic',
    }),
  ],
  // A seção 'css' foi removida, pois a configuração será lida do postcss.config.js
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
  },
});
