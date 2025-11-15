import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import { resolve } from 'path'
const projectRoot = process.env.PROJECT_ROOT || __dirname
export default defineConfig({
  plugins: [tailwindcss()],
  server: { port: Number(process.env.FRONTEND_PORT) || 5000, strictPort: true, host: true },
  resolve: { alias: { '@': resolve(projectRoot, 'src') } },
});
