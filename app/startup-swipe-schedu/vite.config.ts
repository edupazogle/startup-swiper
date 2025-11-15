import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { resolve } from 'path'

const projectRoot = process.env.PROJECT_ROOT || import.meta.dirname

export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/',
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: { port: Number(process.env.FRONTEND_PORT) || 5000, strictPort: true, host: true },
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src')
    }
  },
});
