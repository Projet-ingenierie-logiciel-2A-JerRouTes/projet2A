import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // ✅ On laisse Vite utiliser automatiquement
  // src/frontend/.env, .env.local, etc.
  // (plus de envDir="../../")

  server: {
    // Permet l'accès hors conteneur si besoin
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        // Compatible avec backend Docker (service "backend")
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});