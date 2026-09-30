/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { buildProxy } from "./dev-proxy.ts";

const port = Number.parseInt(process.env["JANE_ADMIN_PORT"] ?? "4600", 10);

export default defineConfig({
  plugins: [react()],
  server: { port, strictPort: true, host: "127.0.0.1", proxy: buildProxy() },
  preview: { port, strictPort: true, host: "127.0.0.1", proxy: buildProxy() },
  build: { outDir: "dist", sourcemap: true, chunkSizeWarningLimit: 2000 },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.{ts,tsx}"],
    setupFiles: ["src/test/setup.ts"],
    css: false,
    testTimeout: 30_000,
  },
});
