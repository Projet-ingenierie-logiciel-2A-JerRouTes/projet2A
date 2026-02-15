import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // On indique à Vite de chercher le .env deux dossiers plus haut (racine du projet)
  envDir: "../../",
});
