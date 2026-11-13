import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// envDir points at the repository root so one .env file configures both apps
export default defineConfig({
  plugins: [react()],
  envDir: "..",
  server: { port: 5173 },
});
