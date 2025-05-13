import { defineConfig, loadEnv } from "vite";

import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default ({ mode }: { mode: string }) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd()) };
  
  return defineConfig({
    plugins: [react()],
    preview: {
      port: parseInt(process.env.VITE_PORT ?? "3000"),
    },
    server: {
      port: parseInt(process.env.VITE_PORT ?? "3000"),
      watch: {
        usePolling: true,
      },
    },
  })
}
