/*import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // On indique à Vite de chercher le .env deux dossiers plus haut (racine du projet)
  envDir: "../../",
});*/


import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // On indique à Vite de chercher le .env deux dossiers plus haut (racine du projet)
  envDir: "../../",
  
  server: {
    // Indispensable pour que le port soit exposé hors du conteneur Docker
    host: true, 
    port: 5173,
    proxy: {
      // Redirige les appels commençant par /api
      '/api': {
        // "backend" correspond au nom du service dans ton docker-compose.yml
        target: 'http://backend:8000', 
        changeOrigin: true,
        // On garde le préfixe /api car ton backend FastAPI semble l'utiliser
        secure: false,
      },
    },
  },
});